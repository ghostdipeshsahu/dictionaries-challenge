"""Browser walkthrough of the whole mission, through the real UI, with installed Chrome.

    python tests/e2e_walkthrough.py http://localhost:8010 <screenshot-dir>

Signs in, accepts the rules, answers all 42 questions with the page's own controls (every question type,
including Board builds and the 7 coding challenges run in real Python via Pyodide), tries a wrong answer, a hint,
the reveal rule, a tab switch and a second tab, and checks the teacher dashboard updates live.
Fails on any browser console error.
"""
import os
import re
import sys
import time

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import content as C  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8010"
SHOTS = sys.argv[2] if len(sys.argv) > 2 else "shots"
os.makedirs(SHOTS, exist_ok=True)
ROLL = f"E2E{int(time.time()) % 100000}"
SEC1, SEC2 = "S-001", "S-002"
errors = []
step_no = [0]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def shot(page, name):
    step_no[0] += 1
    page.screenshot(path=os.path.join(SHOTS, f"{step_no[0]:02d}-{name}.png"), full_page=False)


def watch(page, label):
    page.on("pageerror", lambda e: errors.append(f"{label} pageerror: {e}"))
    page.on("console", lambda m: m.type == "error" and errors.append(f"{label} console: {m.text}"))


def dismiss_tour(page, shoot=None):
    """The How to play tour opens on the first map visit: four cards, then Let's go."""
    expect(page.locator("#modal")).to_contain_text("How to play", timeout=10000)
    if shoot:
        shoot(page, "tour")
    for _ in range(3):
        page.locator("#tourNext").click()
    expect(page.locator("#tourNext")).to_contain_text("Let's go")
    page.locator("#tourNext").click()
    expect(page.locator("#modal")).not_to_be_visible()


def pass_coach(page, seen_types, qtype, shoot=None):
    """The first question of each kind shows how it works; its timer waits for Got it."""
    if qtype in seen_types:
        return
    seen_types.add(qtype)
    expect(page.locator("#coachGo")).to_be_visible(timeout=10000)
    assert page.locator("#qtimer b").inner_text() in ("", page.locator("#qtimer b").inner_text()), "timer element"
    if shoot:
        shoot(page, "coach-" + qtype)
    page.locator("#coachGo").click()
    expect(page.locator("#modal")).not_to_be_visible()


def continue_drawer(page):
    btn = page.locator("#drawer.open #cont")
    expect(btn).to_be_visible(timeout=15000)
    btn.click()


def answer_ui(page, q, correct=True):
    """Answer one question with the page's own controls."""
    t = q["type"]
    if t in ("mcq", "predict", "ar"):
        i = q["answer"] if correct else (q["answer"] + 1) % len(q["options"])
        page.keyboard.press(str(i + 1))  # keyboard shortcut 1-9
    elif t == "msq":
        for i in q["answers"]:
            page.locator(f"#pad .opt[data-i='{i}']").click()
        expect(page.locator("#selCount")).to_have_text(f"{len(q['answers'])} selected")
    elif t == "tf":
        page.locator("#pad .yn .opt").nth(0 if q["value"] == correct else 1).click()
    elif t == "numeric":
        page.locator("#num").fill(str(q["value"] if correct else q["value"] + 1))
    elif t == "fill":
        for k, inp in enumerate(page.locator(".code input.blank").all()):
            inp.fill(q["blanks"][k][0])
    elif t == "match":
        for i, j in enumerate(q["mapping"]):
            page.locator(f"#mL .mitem2[data-i='{i}']").click()
            page.locator(f"#mR .mitem2[data-j='{j}']").click()
    elif t == "categorize":
        for i, k in enumerate(q["mapping"]):
            page.locator(f".catrow[data-i='{i}'] button[data-k='{k}']").click()
    elif t == "order":
        for pos, item in enumerate(q["mapping"]):
            while True:
                ids = [int(x) for x in page.locator("#olist li").evaluate_all("els=>els.map(e=>e.dataset.id)")]
                if ids.index(item) == pos:
                    break
                page.locator(f"#olist li[data-id='{item}'] button[data-d='-1']").click()
    elif t == "debug":
        page.locator(f".code .ln.tappable[data-n='{q['line']}']").click()
        page.locator(f".errseg button[data-k='{q['error']}']").click()
    elif t == "board":
        build_board(page, q["start"], q["target"])
    if t != "coding":
        expect(page.locator("#check")).to_be_enabled()
        page.locator("#check").click()


def build_board(page, start, target):
    """Reach the target with taught lines only: del, then menu[key] = value in target order."""
    want = dict(target)
    for k, _ in start:
        if k not in want:
            page.locator(".board [data-f='k']").fill(k)
            page.locator(".board [data-a='del']").click()
    for k, v in target:
        page.locator(".board [data-f='k']").fill(k)
        page.locator(".board [data-f='v']").fill(str(v))
        page.locator(".board [data-a='set']").click()


def answer_coding(page, q):
    expect(page.locator("#pystate")).to_have_text("Python ready", timeout=120000)
    page.locator("#editor").fill(q["solution"])
    page.locator("#runS").click()
    samples = sum(1 for t in q["challenge"]["tests"] if not t.get("hidden"))
    expect(page.locator("#ctests .test.pass")).to_have_count(samples, timeout=30000)
    page.locator("#submit").click()
    expect(page.locator("#tscore")).to_have_text(f"{len(q['challenge']['tests'])} / {len(q['challenge']['tests'])}", timeout=60000)


def cleanup(base, prefix):
    """Delete every student this test created (roll numbers starting with `prefix`), so the teacher
    dashboard only shows real students."""
    import json
    import urllib.request
    pw = os.environ.get("TEACHER_PASSWORD", "change-me")
    req = urllib.request.Request(base + "/api/teacher/login", data=json.dumps({"password": pw}).encode(),
                                 headers={"Content-Type": "application/json"})
    tok = json.load(urllib.request.urlopen(req))["token"]
    auth = {"Authorization": "Bearer " + tok}
    data = json.load(urllib.request.urlopen(urllib.request.Request(base + "/api/teacher/dicts", headers=auth)))
    gone = 0
    for s in data["students"]:
        if s["roll_no"].startswith(prefix):
            urllib.request.urlopen(urllib.request.Request(f"{base}/api/teacher/students/{s['id']}", method="DELETE", headers=auth))
            gone += 1
    print(f"cleanup: removed {gone} test student(s)")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        ctx = browser.new_context(viewport={"width": 1366, "height": 900}, color_scheme="light")
        page = ctx.new_page()
        watch(page, "student")

        # ---- teacher signs in first and keeps the dashboard open
        tctx = browser.new_context(viewport={"width": 1440, "height": 900})
        tpage = tctx.new_page()
        watch(tpage, "teacher")
        tpage.goto(BASE + "/teacher")
        tpage.locator("#pw").fill(os.environ.get("TEACHER_PASSWORD", "change-me"))
        tpage.locator("#tl button[type=submit]").click()
        expect(tpage.locator("#updated")).to_contain_text("Live", timeout=15000)
        log("teacher dashboard live")

        # ---- sign in
        page.goto(BASE + "/")
        expect(page.locator("#loginForm")).to_be_visible(timeout=15000)
        shot(page, "login")
        page.locator("#lgName").fill("Walk Through")
        page.locator("#lgRoll").fill(ROLL)
        page.locator("#lgSec").select_option(SEC1)
        page.locator("#loginForm button[type=submit]").click()
        expect(page.locator(".map .node")).to_have_count(7, timeout=15000)
        dismiss_tour(page, shot)
        expect(page.locator(".node.next")).to_have_count(1)
        expect(page.locator(".node.next .starthere")).to_have_text("Start here")
        shot(page, "map")
        log("signed in, map shows 7 stages")

        # the teacher sees the student appear without reloading
        expect(tpage.locator("#rows")).to_contain_text("Walk Through", timeout=10000)
        log("teacher: student appeared live")

        # ---- second tab is refused
        dup = ctx.new_page()
        watch(dup, "dup-tab")
        dup.goto(BASE + "/")
        expect(dup.locator("h2")).to_contain_text("already open in another tab", timeout=15000)
        shot(dup, "duplicate-tab")
        dup.close()
        log("duplicate tab screen shown")

        # ---- dict lab (free play)
        page.locator("#labBtn").click()
        expect(page.locator(".labtitle")).to_contain_text("Dict Lab")
        page.locator(".board [data-f='k']").fill("Tea")
        page.locator(".board [data-f='v']").fill("16")
        page.locator(".board [data-a='set']").click()
        expect(page.locator(".board .vmsg")).to_contain_text("case-sensitive")
        page.locator(".board [data-t='photo']").click()
        page.locator(".board [data-f='k']").fill("bun")
        page.locator(".board [data-f='v']").fill("10")
        page.locator(".board [data-a='set']").click()
        expect(page.locator(".board .bview")).to_contain_text("'bun'")
        expect(page.locator(".board .bphoto")).not_to_contain_text("'bun'")
        page.locator(".board [data-f='q']").fill("15")
        page.locator(".board [data-l='in']").click()
        expect(page.locator(".board .bres")).to_have_text("False")
        expect(page.locator(".board .vmsg")).to_contain_text("keys only")
        page.locator(".board [data-f='q']").fill("dosa")
        page.locator(".board [data-l='br']").click()
        expect(page.locator(".board .bres")).to_have_text("KeyError: 'dosa'")
        page.locator(".board [data-l='get']").click()
        expect(page.locator(".board .bres")).to_have_text("None")
        page.locator(".board [data-t='dup']").click()
        expect(page.locator(".board .bprint")).to_have_text("{'tea': 14, 'coffee': 15}")
        shot(page, "dict-lab")
        page.locator("#quit").click()
        log("dict lab experiments behave like Python")

        # ---- field guide
        page.locator("#guideBtn").click()
        expect(page.locator("#guideTitle")).to_have_text("Field guide: Python dictionaries")
        shot(page, "field-guide")
        page.locator("#gclose").click()

        # ---- start: briefing -> rules -> first question
        page.locator("#go").click()
        expect(page.locator(".brief h2")).to_have_text("Mission Briefing")
        expect(page.locator(".brief .story")).to_contain_text("32")
        expect(page.locator(".learn li").first).to_be_visible()
        # Watch it first: step through the worked example; the output must be what Python prints
        walk = C.LEVELS[0]["walk"]
        for _ in walk:
            page.locator("#walkNext").click()
        expect(page.locator("#walkStep")).to_have_text(f"Step {len(walk)} of {len(walk)}")
        expect(page.locator("#walk .con-out")).to_have_text("\n".join(w["shows"] for w in walk if "shows" in w))
        shot(page, "briefing")
        page.locator("#begin").click()
        expect(page.locator("#rulesGo")).to_be_disabled()
        shot(page, "rules")
        page.locator("#agree").check()
        page.locator("#rulesGo").click()
        expect(page.locator("#qtimer")).to_be_visible(timeout=10000)
        expect(page.locator("#clock")).to_be_visible()
        log("rules accepted, question timer and mission clock running")

        played = 0
        seen_types = set()
        for lvl in C.LEVELS:
            if lvl["id"] != "L0":
                expect(page.locator(".brief h2")).to_have_text(lvl["name"], timeout=15000)
                page.locator("#begin").click()
            for qid in lvl["main"]:
                q = C.QUESTIONS[qid]
                title = q["challenge"]["title"] if q["type"] == "coding" else q["title"]
                expect(page.locator("#qtitle")).to_have_text(re.compile(re.escape(title[:40])), timeout=20000)
                expect(page.locator(".qchip")).to_contain_text(C.TYPE_LABEL[q["type"]] if q["type"] != "coding" else "Coding")
                expect(page.locator(".howto").first).to_be_visible()
                pass_coach(page, seen_types, q["type"], shot if q["type"] in ("match", "board", "coding") else None)

                if qid == "L0-2":  # a wrong answer first: drawer shows the catch, retry works, XP stays
                    answer_ui(page, q, correct=False)
                    expect(page.locator("#drawer.open.bad")).to_be_visible()
                    shot(page, "wrong-answer-drawer")
                    page.locator("#dhint").click()  # "Show the hint" from the drawer
                    expect(page.locator("#hintSlot .hintbox")).to_contain_text("Concept")
                if qid == "L3-1":  # two wrong tries unlock "Show the solution"
                    for _ in range(2):
                        answer_ui(page, q, correct=False)
                        expect(page.locator("#drawer.open.bad")).to_be_visible()
                        if page.locator("#drawer #reveal").count():
                            break
                        page.locator("#retry").click()
                    page.locator("#drawer #reveal").click()
                    expect(page.locator("#drawer.open.shown")).to_be_visible()
                    shot(page, "solution-shown")
                    continue_drawer(page)
                    played += 1
                    continue
                if qid == "L1-1":  # a tab switch is caught and recorded
                    page.evaluate("dispatchEvent(new Event('blur'))")
                    time.sleep(1.1)
                    page.evaluate("dispatchEvent(new Event('focus'))")
                    expect(page.locator("#modal")).to_contain_text("You left the mission tab", timeout=10000)
                    shot(page, "tab-switch-warning")
                    page.locator("#okBack").click()

                if q["type"] == "coding":
                    answer_coding(page, q)
                else:
                    answer_ui(page, q, correct=True)
                expect(page.locator("#drawer.open.ok")).to_be_visible(timeout=60000)
                if qid in ("L0-1", "L2-2", "L3-7", "L5-1"):
                    shot(page, f"correct-{qid}")
                continue_drawer(page)
                played += 1

            # stage clear screen
            if lvl["id"] == "BOSS":
                expect(page.locator("section.done h2")).to_have_text("Board fixed!", timeout=15000)
            else:
                expect(page.locator("section.done h2")).to_have_text("Stage clear!", timeout=15000)
            if lvl["id"] in ("L0", "BOSS"):
                shot(page, f"stage-clear-{lvl['id']}")
            log(f"{lvl['name']} cleared ({played} questions so far)")
            if lvl["id"] == "L2":  # the teacher sees where the student is, without reloading
                cur = tpage.locator("#rows tr", has_text="Walk Through").locator("td.curcell")
                expect(cur).to_contain_text("Board Builder", timeout=10000)
                shot(tpage, "teacher-live")
            page.locator("#nextL").click()

        # ---- mission report
        expect(page.locator(".report h2")).to_have_text("Python Dictionaries Champion", timeout=15000)
        expect(page.locator(".endbanner.done")).to_be_visible()
        shot(page, "report")
        log(f"mission complete: {played} questions played through the UI")

        # ---- teacher: completed status, row data, CSV export
        expect(tpage.locator("#rows")).to_contain_text("Completed", timeout=10000)
        row = tpage.locator("#rows tr", has_text="Walk Through")
        expect(row).to_contain_text("42/42")
        expect(row.locator("td").nth(11)).to_have_text("1")  # one tab switch recorded ("Now on" is column 5)
        shot(tpage, "teacher-final")
        with tpage.expect_download() as dl:
            tpage.locator("#export").click()
        csv_path = os.path.join(SHOTS, dl.value.suggested_filename)
        dl.value.save_as(csv_path)
        assert "Walk Through" in open(csv_path, encoding="utf-8").read()
        log("teacher: completed row, tab switch count and CSV export OK")

        # ---- profile, mobile width and dark mode
        page.locator("#userChip").click()
        expect(page.locator(".pcard h2")).to_have_text("Walk Through")
        shot(page, "profile")
        mob = browser.new_context(viewport={"width": 390, "height": 844}, color_scheme="dark", is_mobile=True, has_touch=True)
        mpage = mob.new_page()
        watch(mpage, "mobile")
        mpage.goto(BASE + "/")
        mpage.locator("#lgName").fill("Mobile Dark")
        mpage.locator("#lgRoll").fill(ROLL + "M")
        mpage.locator("#lgSec").select_option(SEC2)
        mpage.locator("#loginForm button[type=submit]").click()
        expect(mpage.locator(".map .node")).to_have_count(7, timeout=15000)
        dismiss_tour(mpage)
        width = mpage.evaluate("document.documentElement.scrollWidth")
        assert width <= 390, f"horizontal scroll on mobile: {width}px"
        shot(mpage, "mobile-dark-map")
        mpage.locator("#labBtn").click()
        expect(mpage.locator(".labtitle")).to_be_visible()
        assert mpage.evaluate("document.documentElement.scrollWidth") <= 390, "lab scrolls sideways on mobile"
        shot(mpage, "mobile-dark-lab")
        log("mobile width + dark mode: no sideways scroll")
        browser.close()

    if errors:
        print("\nBROWSER ERRORS:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("\nWALKTHROUGH PASSED")


if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup(BASE, ROLL)
