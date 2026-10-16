"""Browser check of the two clocks. Run against a server started with MISSION_MINUTES=1.

    MISSION_MINUTES=1 DB_PATH=data/timers.db uvicorn app.main:app --port 8011
    python tests/e2e_timers.py http://localhost:8011 <screenshot-dir>

1. A question countdown reaches half time (hint nudge) and then zero (time-up drawer with the answer).
2. The mission clock reaches zero: the mission ends and the report says time is up.
"""
import os
import sys
import time

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from e2e_walkthrough import dismiss_tour, pass_coach, send_feedback  # noqa: E402
from app import content as C  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8011"
SHOTS = sys.argv[2] if len(sys.argv) > 2 else "shots-timers"
os.makedirs(SHOTS, exist_ok=True)
errors = []
ROLL = f"TMR{int(time.time()) % 100000}"


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


try:
  with sync_playwright() as p:
      b = p.chromium.launch(channel="chrome", headless=True)
      page = b.new_page(viewport={"width": 1366, "height": 900})
      page.on("pageerror", lambda e: errors.append(str(e)))
      page.on("console", lambda m: m.type == "error" and errors.append(m.text))
      page.goto(BASE + "/")
      page.locator("#lgName").fill("Timer Check")
      page.locator("#lgRoll").fill(ROLL)
      page.locator("#lgSec").select_option("S-001")
      page.locator("#loginForm button[type=submit]").click()
      dismiss_tour(page)
      page.locator("#go").click()
      page.locator("#begin").click()
      page.locator("#agree").check()
      page.locator("#rulesGo").click()
      pass_coach(page, set(), "mcq")
      expect(page.locator("#clockNum")).to_have_text("1:00", timeout=5000)

      # L0-1 has a 45-second countdown; the hint nudge appears at half time
      expect(page.locator("#qtimer")).to_be_visible()
      expect(page.locator("#hintSlot .nudgeline")).to_be_visible(timeout=30000)
      expect(page.locator("#hint")).to_have_class("btn ghost nudge")
      print("half-time hint nudge shown")
      expect(page.locator("#qtimer")).to_have_class("qtimer low", timeout=20000)  # red under 10 s
      page.screenshot(path=os.path.join(SHOTS, "01-question-timer-low.png"))
      expect(page.locator("#drawer.open.timeup")).to_be_visible(timeout=20000)
      expect(page.locator("#drawer .dr-ans")).to_contain_text(C.QUESTIONS["L0-1"]["options"][C.QUESTIONS["L0-1"]["answer"]])
      page.screenshot(path=os.path.join(SHOTS, "02-time-up-drawer.png"))
      print("time-up drawer shows the answer")
      page.locator("#cont").click()

      # mission clock: red under 5 minutes, then the mission ends on its own
      expect(page.locator("#clock")).to_have_class("stat clock low")
      expect(page.locator(".survey .endbanner.time")).to_contain_text("Time's up", timeout=40000)  # feedback first
      send_feedback(page)
      expect(page.locator(".report h2")).to_have_text("Mission over", timeout=15000)
      expect(page.locator(".endbanner.time")).to_contain_text("Time's up")
      page.screenshot(path=os.path.join(SHOTS, "03-mission-time-up.png"))
      print("mission clock ended the mission and the report says so")
      b.close()

finally:
    cleanup(BASE, ROLL)

if errors:
    print("BROWSER ERRORS:", errors)
    sys.exit(1)
print("TIMERS PASSED")
