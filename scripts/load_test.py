"""Load test against the live site: 30 students at once, like a class, plus a teacher dashboard polling every 5 s.

Each simulated student signs in, starts, plays through the stages with 1-3 s of "thinking" between steps
(some wrong answers, heartbeats), then either clears the whole mission or ends on tab switches, and sends the
feedback. Afterwards it checks that the dashboard and the CSV hold every student, answer and feedback, then
deletes all the test students (roll numbers LOADT...).

    LOADTEST_TEACHER_PW=<teacher password> python scripts/load_test.py https://<your-site>.vercel.app 70

The site's /api/health says which session it runs, so the same script tests Session 29 and Session 30.
Run it before a class, never while real students are using the site. Needs: pip install httpx
"""
import csv
import io
import os
import random
import statistics
import sys
import threading
import time
from collections import defaultdict

from pathlib import Path

import httpx

BASE = sys.argv[1].rstrip("/")
# load the same session's questions as the site runs, to send right (and some wrong) answers
os.environ["MISSION"] = httpx.get(BASE + "/api/health", timeout=60).json()["mission"]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import content as C  # noqa: E402

N = int(sys.argv[2]) if len(sys.argv) > 2 else 30
PW = os.environ["LOADTEST_TEACHER_PW"]
PREFIX = f"LOADT{int(time.time()) % 10000:04d}-"
LAT = defaultdict(list)          # endpoint -> seconds
ERR = []                          # (student, endpoint, status, body)
LOCK = threading.Lock()
EXPECT = {}                       # roll -> {"done": n, "status": s}
stop_teacher = threading.Event()


def right(q):
    t = q["type"]
    if t in ("mcq", "predict", "ar"):
        return q["answer"]
    if t == "msq":
        return q["answers"]
    if t in ("tf", "numeric"):
        return q["value"]
    if t == "fill":
        return [b[0] for b in q["blanks"]]
    if t in ("match", "order", "categorize", "land"):
        return q["mapping"]
    if t == "debug":
        return {"line": q["line"], "error": q["error"]}
    if t == "board":
        return {"rows": q["target"]}
    if t == "coding":
        return {"outputs": [{"stdout": tt["expected"] + "\n", "error": None} for tt in q["challenge"]["tests"]]}


def wrong(q):
    t = q["type"]
    if t in ("mcq", "predict", "ar"):
        return (q["answer"] + 1) % len(q["options"])
    if t == "tf":
        return not q["value"]
    if t == "numeric":
        return q["value"] + 1
    return None


def call(c, who, method, path, body=None, ok=(200,)):
    t0 = time.perf_counter()
    try:
        r = c.request(method, BASE + path, json=body)
    except Exception as e:  # network error / timeout
        with LOCK:
            ERR.append((who, path, "network", repr(e)[:120]))
        return None
    dt = time.perf_counter() - t0
    key = path.split("?")[0]
    key = "/api/teacher/students/{id}" if key.startswith("/api/teacher/students/") else key
    with LOCK:
        LAT[f"{method} {key}"].append(dt)
        if r.status_code not in ok:
            ERR.append((who, path, r.status_code, r.text[:160]))
    return r


def student(i):
    roll = f"{PREFIX}{i:02d}"
    who = roll
    finish_all = i % 2 == 0            # half clear everything, half end on tab switches part-way
    time.sleep(random.uniform(0, 10))  # a class signs in over ~10 seconds
    with httpx.Client(timeout=30) as c:
        call(c, who, "GET", "/api/health")
        r = call(c, who, "POST", "/api/login", {"name": f"Load Test {i:02d}", "roll_no": roll, "section": "LOADTEST",
                                                 "university": "Load Test University", "contact": f"9{random.randint(100000000, 999999999)}"})
        if not r or r.status_code != 200:
            return
        c.headers["Authorization"] = "Bearer " + r.json()["token"]
        call(c, who, "GET", "/api/me")
        call(c, who, "GET", "/api/dicts/mission")
        call(c, who, "POST", "/api/dicts/start", {"accept_rules": True})
        levels = [l for l in C.LEVELS if not l.get("bonus")]
        stop_after = len(levels) if finish_all else random.randint(2, 4)
        done = 0
        last_ping = time.time()
        for lvl in levels[:stop_after]:
            for qid in lvl["main"]:
                q = C.QUESTIONS[qid]
                call(c, who, "POST", "/api/dicts/open", {"qid": qid})
                time.sleep(random.uniform(1, 3))
                w = wrong(q)
                if w is not None and random.random() < 0.25:   # a wrong first try now and then
                    call(c, who, "POST", "/api/dicts/answer", {"qid": qid, "answer": w})
                    time.sleep(random.uniform(0.5, 1.5))
                r = call(c, who, "POST", "/api/dicts/answer", {"qid": qid, "answer": right(q), "code": q.get("solution")})
                if r and r.status_code == 200 and r.json().get("correct"):
                    done += 1
                elif r is not None:
                    with LOCK:
                        ERR.append((who, f"answer {qid}", r.status_code, r.text[:160]))
                if time.time() - last_ping > 25:
                    call(c, who, "POST", "/api/ping")
                    last_ping = time.time()
        if finish_all:
            call(c, who, "POST", "/api/dicts/finish")      # skip the optional bonus round
        else:
            for _ in range(3):
                call(c, who, "POST", "/api/dicts/proctor", {"type": "tab_switch", "duration_ms": 2000})
                time.sleep(0.3)
        st = call(c, who, "GET", "/api/dicts/mission")
        ended = st is not None and st.status_code == 200 and st.json()["state"]["ended_at"]
        if ended:
            call(c, who, "GET", "/api/dicts/review")
            call(c, who, "GET", "/api/dicts/leaderboard")
            stages = [l["id"] for l in levels]
            call(c, who, "POST", "/api/dicts/feedback", {
                "enjoy": random.randint(2, 5), "toughest": random.choice(stages), "favourite": random.choice(stages),
                "difficulty": random.choice(["easy", "right", "hard"]), "pace": random.choice(["spare", "enough", "more"]),
                "confidence": random.randint(1, 5), "helped": random.sample([k for k, _, _ in C.FEEDBACK_HELPED], 2),
                "tech": "no", "improve": f"load test {i}"})
        with LOCK:
            EXPECT[roll] = {"done": done, "status": "complete" if finish_all else "proctor", "feedback": bool(ended)}


def teacher(tok):
    with httpx.Client(timeout=30, headers={"Authorization": "Bearer " + tok}) as c:
        while not stop_teacher.is_set():
            call(c, "teacher", "GET", "/api/teacher/dicts")
            stop_teacher.wait(5)


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))]


def main():
    with httpx.Client(timeout=30) as c:
        r = c.post(BASE + "/api/teacher/login", json={"password": PW})
        if r.status_code != 200:
            sys.exit(f"teacher login failed ({r.status_code}): nothing was created")
        tok = r.json()["token"]
    try:
        run(tok)
    finally:
        cleanup(tok)


def cleanup(tok):
    """Delete every load-test student (also ones left by an earlier, interrupted run)."""
    with httpx.Client(timeout=120, headers={"Authorization": "Bearer " + tok}) as c:
        d = c.get(BASE + "/api/teacher/dicts").json()
        test = [s for s in d["students"] if s["roll_no"].startswith("LOADT") and s["section"] == "LOADTEST"]
        removed = sum(c.delete(f"{BASE}/api/teacher/students/{s['id']}").status_code == 200 for s in test)
        left = [s for s in c.get(BASE + "/api/teacher/dicts").json()["students"] if s["roll_no"].startswith("LOADT")]
        print(f"cleanup: removed {removed} test students, {len(left)} left", flush=True)


def run(tok):
    tt = threading.Thread(target=teacher, args=(tok,))
    tt.start()
    t0 = time.time()
    threads = [threading.Thread(target=student, args=(i + 1,)) for i in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stop_teacher.set()
    tt.join()
    wall = time.time() - t0

    total = sum(len(v) for v in LAT.values())
    print(f"\n=== {N} students at once against {BASE} · {total} requests in {wall:.0f} s · {len(ERR)} errors ===")
    print(f"{'endpoint':38} {'n':>5} {'p50':>7} {'p95':>7} {'max':>7}")
    for k in sorted(LAT, key=lambda k: -len(LAT[k])):
        v = LAT[k]
        print(f"{k:38} {len(v):5d} {statistics.median(v)*1000:6.0f}ms {pct(v, 95)*1000:6.0f}ms {max(v)*1000:6.0f}ms")
    allv = [x for v in LAT.values() for x in v]
    print(f"{'ALL':38} {len(allv):5d} {statistics.median(allv)*1000:6.0f}ms {pct(allv, 95)*1000:6.0f}ms {max(allv)*1000:6.0f}ms")
    for e in ERR[:15]:
        print("ERROR", e)

    # ---- is every student, answer and feedback saved?
    with httpx.Client(timeout=60, headers={"Authorization": "Bearer " + tok}) as c:
        d = c.get(BASE + "/api/teacher/dicts").json()
        mine = {s["roll_no"]: s for s in d["students"] if s["roll_no"].startswith(PREFIX)}
        fb = {f["roll_no"] for f in d["feedback"]["responses"] if f["roll_no"].startswith(PREFIX)}
        bad = []
        for roll, exp in EXPECT.items():
            s = mine.get(roll)
            if not s:
                bad.append((roll, "missing from dashboard"))
            elif s["done"] != exp["done"] or s["status"] != exp["status"]:
                bad.append((roll, f"dashboard {s['done']} {s['status']} vs expected {exp['done']} {exp['status']}"))
            if exp["feedback"] and roll not in fb:
                bad.append((roll, "feedback missing"))
        rows = list(csv.DictReader(io.StringIO(c.get(BASE + "/api/teacher/dicts/export.csv").text.lstrip("\ufeff"))))
        csv_mine = [r for r in rows if r["roll_no"].startswith(PREFIX)]
        print(f"\n=== data check ===\nstudents finished: {len(EXPECT)}/{N} · on dashboard: {len(mine)} · "
              f"answers expected {sum(e['done'] for e in EXPECT.values())}, on dashboard {sum(s['done'] for s in mine.values())} · "
              f"feedback {len(fb)}/{sum(e['feedback'] for e in EXPECT.values())} · CSV rows {len(csv_mine)} "
              f"(with feedback {sum(r['feedback_sent'] == 'yes' for r in csv_mine)})")
        print("mismatches:", bad[:10] or "none")

main()
