"""Browser check: tab-switch end -> teacher Resume -> student continues by itself; idle students are flagged.
Run against a throwaway server with a short idle threshold:

    IDLE_SECONDS=20 DB_PATH=data/scratch.db uvicorn app.main:app --port 8012
    python tests/e2e_resume.py http://localhost:8012 <screenshot-dir>
"""
import os
import sys
import time

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, os.path.dirname(__file__))
from e2e_walkthrough import cleanup, dismiss_tour, pass_coach  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8012"
SHOTS = sys.argv[2] if len(sys.argv) > 2 else "shots-resume"
os.makedirs(SHOTS, exist_ok=True)
ROLL = f"RSM{int(time.time()) % 100000}"
errors = []


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, name + ".png"))


def leave_tab(page):
    page.evaluate("dispatchEvent(new Event('blur'))")
    time.sleep(1.1)
    page.evaluate("dispatchEvent(new Event('focus'))")


try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        tpage = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
        page = b.new_context(viewport={"width": 1366, "height": 900}).new_page()
        for pg, label in ((tpage, "teacher"), (page, "student")):
            pg.on("pageerror", lambda e, l=label: errors.append(f"{l}: {e}"))
            pg.on("console", lambda m, l=label: m.type == "error" and errors.append(f"{l}: {m.text}"))
        tpage.goto(BASE + "/teacher")
        tpage.locator("#pw").fill(os.environ.get("TEACHER_PASSWORD", "change-me"))
        tpage.locator("#tl button[type=submit]").click()
        expect(tpage.locator("#pAttn")).to_contain_text("Everyone is moving", timeout=15000)

        page.goto(BASE + "/")
        page.locator("#lgName").fill("Resume Check")
        page.locator("#lgRoll").fill(ROLL)
        page.locator("#lgSec").select_option("S-001")
        page.locator("#loginForm button[type=submit]").click()
        dismiss_tour(page)
        page.locator("#go").click()
        page.locator("#begin").click()
        page.locator("#agree").check()
        page.locator("#rulesGo").click()
        pass_coach(page, set(), "mcq")
        expect(page.locator("#pad .opt")).to_have_count(4, timeout=10000)
        expect(page.locator("#modal")).not_to_be_visible()
        page.keyboard.press("1")
        expect(page.locator("#check")).to_be_enabled()
        page.locator("#check").click()
        page.locator("#drawer.open #cont").click()            # L0-1 solved, now on L0-2
        expect(page.locator("#qtitle")).to_contain_text("True or false")
        pass_coach(page, {"mcq"}, "tf")                       # first True/False: its timer starts after Got it
        time.sleep(4)                                         # spend a few seconds on the question

        # 1) three tab switches end the mission
        for i in range(3):
            leave_tab(page)
            if i < 2:
                expect(page.locator("#modal")).to_contain_text("You left the mission tab", timeout=10000)
                page.locator("#okBack").click()
        expect(page.locator(".endbanner.proctor")).to_be_visible(timeout=15000)
        expect(page.locator("#resumeWait")).to_be_visible()
        shot(page, "02-student-waiting")
        print("mission ended on tab switches; student waits for the teacher")

        # 2) the teacher resumes from the attention panel (tap twice)
        btn = tpage.locator("#pAttn .del[data-a='resume']")
        expect(btn).to_be_visible(timeout=15000)
        expect(tpage.locator("#pAttn")).to_contain_text("left the tab 3 times")
        shot(tpage, "03-teacher-resume")
        btn.click()
        expect(btn).to_have_text("Tap again: resume")
        btn.click()
        expect(tpage.locator("#pAttn")).not_to_contain_text("left the tab", timeout=10000)
        print("teacher pressed Resume")

        # 3) the student page continues on its own (no reload, no click)
        expect(page.locator(".map .node")).to_have_count(7, timeout=12000)
        expect(page.locator(".toast")).to_contain_text("resumed", timeout=5000)
        shot(page, "04-student-resumed")
        page.locator("#go").click()
        page.locator("#begin").click()
        expect(page.locator("#qtitle")).to_contain_text("True or false")  # back on L0-2; L0-1 stays solved
        left = page.locator("#qtime").inner_text()
        mm, ss = left.split(":")
        secs = int(mm) * 60 + int(ss)
        # L0-2 has 30 s; a few were used before the tab switches, and the minutes spent ended are not counted
        assert 10 < secs <= 27, f"L0-2 should keep its remaining seconds (about 25 of 30), shows {left}"
        assert page.locator("#xpNum").inner_text() != "0", "XP was kept"
        print(f"student back on the same question with {left} left and XP kept")
        # 4) idle: no step for 20 s -> the teacher sees it
        expect(tpage.locator("#pAttn")).to_contain_text("Not moving for", timeout=40000)
        expect(tpage.locator("#rows .atag.idle")).to_be_visible()
        shot(tpage, "01-teacher-idle")
        print("teacher sees the idle student")

        b.close()
finally:
    cleanup(BASE, ROLL)

if errors:
    print("BROWSER ERRORS:", errors)
    sys.exit(1)
print("RESUME PASSED")
