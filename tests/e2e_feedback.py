"""Browser check: when the mission clock runs out the feedback opens by itself, cannot be skipped, keeps a draft
across a reload, and reaches the teacher dashboard. Run against a throwaway server with a 1-minute mission:

    MISSION_MINUTES=1 DB_PATH=data/scratch.db uvicorn app.main:app --port 8012
    python tests/e2e_feedback.py http://localhost:8012 <screenshot-dir>
"""
import os
import sys
import time

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, os.path.dirname(__file__))
from e2e_walkthrough import cleanup, dismiss_tour  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8012"
SHOTS = sys.argv[2] if len(sys.argv) > 2 else "shots-feedback"
os.makedirs(SHOTS, exist_ok=True)
ROLL = f"FBK{int(time.time()) % 100000}"
errors = []


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, name + ".png"))


def must_fill_first(page, text):
    page.locator("#svNext").click()
    expect(page.locator("#svErr")).to_contain_text(text)


try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        page = b.new_context(viewport={"width": 1366, "height": 900}).new_page()
        page.on("pageerror", lambda e: errors.append(f"student: {e}"))
        page.on("console", lambda m: m.type == "error" and errors.append(f"student: {m.text}"))
        page.goto(BASE + "/")
        page.locator("#lgName").fill("Feedback Check")
        page.locator("#lgRoll").fill(ROLL)
        page.locator("#lgSec").fill("S-001")
        page.locator("#lgUni").fill("Test University")
        page.locator("#loginForm button[type=submit]").click()
        dismiss_tour(page)
        page.locator("#go").click()
        page.locator("#begin").click()
        page.locator("#agree").check()
        page.locator("#rulesGo").click()
        expect(page.locator("#pad")).to_be_visible(timeout=10000)

        # 1) the clock runs out: the feedback opens by itself, with the "progress is saved" banner
        expect(page.locator(".survey")).to_be_visible(timeout=90000)
        expect(page.locator(".endbanner.time")).to_contain_text("progress is saved")
        expect(page.locator("#svBack")).to_have_count(0)
        shot(page, "01-time-up-about-you")
        print("time ran out: feedback opened by itself")

        # 2) about you: name and roll come from the login, the rest is required
        must_fill_first(page, "university")
        expect(page.locator("#svUni")).to_have_count(0)            # the university comes from the sign-in
        expect(page.locator(".svgrid input[readonly]").nth(2)).to_have_value("Test University")
        page.locator("#svPhone").fill("98765 43210")
        page.locator("#svNext").click()

        # 3) enjoyment faces
        must_fill_first(page, "Tap a face")
        page.locator(".face[data-v='5']").click()
        expect(page.locator("#faceLab")).to_have_text("Loved it")
        shot(page, "02-enjoy")
        page.locator("#svNext").click()

        # 4) the instructor: 5 throws, roses or tomatoes
        must_fill_first(page, "Throw all 5")
        for kind in ("tRose", "tTom", "tRose", "tRose", "tTom"):
            page.locator("#" + kind).click()
            page.wait_for_timeout(750)
        expect(page.locator("#ammo span")).to_have_text("All thrown!")
        expect(page.locator("#tRose")).to_be_disabled()
        expect(page.locator("#splats .splat")).to_have_count(2)
        expect(page.locator("#pile .rosep")).to_have_count(3)
        page.locator("#svNote").fill("Loved the canteen examples")
        page.wait_for_timeout(500)
        shot(page, "03-instructor-throws")
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(400)
        shot(page, "03b-instructor-phone")
        page.set_viewport_size({"width": 1366, "height": 900})

        # a reload keeps the draft, and the report stays locked until the feedback is sent
        page.reload()
        expect(page.locator(".survey")).to_be_visible(timeout=15000)
        expect(page.locator("#splats .splat")).to_have_count(2)
        expect(page.locator("#svNote")).to_have_value("Loved the canteen examples")
        page.locator("#homeBtn").click()
        expect(page.locator(".survey")).to_be_visible()
        print("reload kept the draft; the map stays locked")
        page.locator("#svNext").click()

        # 5) difficulty and confidence
        must_fill_first(page, "difficulty")
        page.locator(".bigopt[data-k='right']").click()
        page.locator(".mbar[data-v='4']").click()
        expect(page.locator(".mbar.on")).to_have_count(4)
        shot(page, "04-difficulty-confidence")
        page.locator("#svNext").click()

        # 6) what helped
        must_fill_first(page, "at least one")
        page.locator(".chip").nth(0).click()
        page.locator(".chip").nth(3).click()
        shot(page, "05-helped")
        page.locator("#svNext").click()

        # 7) technical problems and the send
        must_fill_first(page, "technical")
        page.locator(".bigopt[data-k='no']").click()
        page.locator("#svImp").fill("More coding questions please")
        shot(page, "06-tech-improve")
        page.locator("#svNext").click()
        expect(page.locator(".thanks")).to_be_visible(timeout=10000)
        shot(page, "07-thanks")
        expect(page.locator(".report")).to_be_visible(timeout=10000)
        expect(page.locator(".endbanner.time")).to_be_visible()
        print("feedback sent; the report opened")

        # 8) the teacher sees it
        tpage = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
        tpage.on("pageerror", lambda e: errors.append(f"teacher: {e}"))
        tpage.goto(BASE + "/teacher")
        tpage.locator("#pw").fill(os.environ.get("TEACHER_PASSWORD", "change-me"))
        tpage.locator("#tl button[type=submit]").click()
        expect(tpage.locator("#fbCount")).to_have_text("1", timeout=15000)
        expect(tpage.locator("#pFb")).to_contain_text("More coding questions please")
        expect(tpage.locator("#pFb")).to_contain_text("Loved the canteen examples")
        tpage.locator(".fball summary").click()
        expect(tpage.locator(".fball tbody")).to_contain_text("9876543210")
        expect(tpage.locator("#rows")).to_contain_text("feedback sent")
        tpage.locator("#fbPanel").scroll_into_view_if_needed()
        tpage.locator("#fbPanel").screenshot(path=os.path.join(SHOTS, "08-teacher-feedback.png"))
        with tpage.expect_download() as dl:
            tpage.locator("#fbExport").click()
        assert "Test University" in open(dl.value.path(), encoding="utf-8-sig").read()
        print("teacher sees the feedback and downloads the CSV")
        b.close()
finally:
    cleanup(BASE, ROLL)

if errors:
    print("BROWSER ERRORS:", errors)
    sys.exit(1)
print("FEEDBACK PASSED")
