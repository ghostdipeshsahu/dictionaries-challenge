"""Backend tests: login, start, timers, expire, hint cost, reveal rule, XP rules, combo, stars, badges,
proctor limits, reset / release / delete, CSV export, and a full playthrough.

    python -m pytest -q tests
"""
import json
import os
import sys
import time as real_time

import pytest

os.environ["DB_PATH"] = ":memory:"
os.environ.setdefault("TEACHER_PASSWORD", "test-pass")
os.environ["SECTIONS"] = "Section A,Section B,Section C,Section D"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient  # noqa: E402

from app import content as C  # noqa: E402
from app import db, engine, main  # noqa: E402


class FakeTime:
    """Stands in for the `time` module inside the app, so tests can move the clock."""

    def __init__(self):
        self.t = 1_800_000_000.0
        self.strftime, self.gmtime = real_time.strftime, real_time.gmtime

    def time(self):
        return self.t


@pytest.fixture()
def clock(monkeypatch):
    ft = FakeTime()
    for mod in (engine, main, db):
        monkeypatch.setattr(mod, "time", ft)
    return ft


@pytest.fixture()
def client(clock):
    db.connect(":memory:")
    main.TEACHER_PASSWORD = "test-pass"
    return TestClient(main.app)


_roll = [0]


def login(client, name="Ravi Kumar", section="Section A", roll=None):
    _roll[0] += 1
    r = client.post("/api/login", json={"name": name, "roll_no": roll or f"R{_roll[0]:03d}", "section": section})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["token"]}


def teacher(client):
    r = client.post("/api/teacher/login", json={"password": "test-pass"})
    assert r.status_code == 200
    return {"Authorization": "Bearer " + r.json()["token"]}


def start(client, h):
    r = client.post("/api/dicts/start", json={"accept_rules": True}, headers=h)
    assert r.status_code == 200, r.text
    return r.json()["state"]


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
    if t in ("match", "order", "categorize"):
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
    if t == "numeric":
        return q["value"] + 1
    if t == "tf":
        return not q["value"]
    if t == "msq":
        return [i for i in range(len(q["options"])) if i not in q["answers"]][:1]
    raise AssertionError(t)


def ans(client, h, qid, a, code=None, open_first=True):
    if open_first:
        assert client.post("/api/dicts/open", json={"qid": qid}, headers=h).status_code == 200
    body = {"qid": qid, "answer": a}
    if code is not None:
        body["code"] = code
    return client.post("/api/dicts/answer", json=body, headers=h)


def solve(client, h, qid):
    q = C.QUESTIONS[qid]
    r = ans(client, h, qid, right(q), code=q.get("solution"))
    assert r.status_code == 200 and r.json()["correct"], (qid, r.text)
    return r.json()


def clear_stage(client, h, lid):
    for qid in C.LEVEL_BY_ID[lid]["main"]:
        solve(client, h, qid)


# ---------------------------------------------------------------- sign-in
def test_health_and_sections(client):
    r = client.get("/api/health").json()
    assert r["ok"] and r["sections"] and r["class_code_required"] is False


def test_login_validation(client):
    assert client.post("/api/login", json={"name": "A", "roll_no": "1", "section": "Nope"}).status_code == 422
    assert client.post("/api/login", json={"name": " ", "roll_no": "1", "section": "Section A"}).status_code == 422


def test_one_device_at_a_time_and_release(client, clock):
    h1 = login(client, roll="X1")
    r = client.post("/api/login", json={"name": "Ravi Kumar", "roll_no": "x1", "section": "Section A"})
    assert r.status_code == 409 and "another device" in r.json()["detail"]
    # same roll number, different name: refused
    assert client.post("/api/login", json={"name": "Someone", "roll_no": "X1", "section": "Section A"}).status_code == 409
    # teacher releases the login: old device is signed out, a new device can sign in
    sid = client.get("/api/me", headers=h1).json()["student"]["id"]
    t = teacher(client)
    assert client.post(f"/api/teacher/students/{sid}/release", headers=t).status_code == 200
    assert client.post("/api/ping", headers=h1).status_code == 401
    assert client.post("/api/login", json={"name": "ravi kumar", "roll_no": "X1", "section": "Section A"}).status_code == 200


def test_device_lock_expires_without_heartbeat(client, clock):
    login(client, roll="X2")
    clock.t += main.DEVICE_LOCK + 1
    assert client.post("/api/login", json={"name": "Ravi Kumar", "roll_no": "X2", "section": "Section A"}).status_code == 200


def test_logout(client):
    h = login(client)
    assert client.post("/api/logout", headers=h).status_code == 200
    assert client.get("/api/me", headers=h).status_code == 401


# ---------------------------------------------------------------- answer keys never leak
SECRET_KEYS = {"answer", "answers", "value", "blanks", "mapping", "line", "error", "target", "why", "solution", "rules", "hints", "explain", "trap"}


def test_mission_payload_has_no_answer_keys(client):
    h = login(client)
    m = client.get("/api/dicts/mission", headers=h).json()
    assert len(m["levels"]) == 7 and sum(len(l["questions"]) for l in m["levels"]) == 42
    for l in m["levels"]:
        for q in l["questions"]:
            assert not (SECRET_KEYS & set(q)), (q["id"], SECRET_KEYS & set(q))
            if q["type"] == "coding":
                for t in q["challenge"]["tests"]:
                    assert ("expected" in t) == (not t["hidden"])
    blob = json.dumps(m)
    for q in C.QUESTIONS.values():
        if q["type"] == "coding":
            # hidden expected outputs are checked structurally above (no "expected" field); a text
            # search would also hit identical boards that are ordinary options in other questions
            assert json.dumps(q["solution"])[1:-1] not in blob, q["id"]


def test_wrong_answer_does_not_reveal_key(client):
    h = login(client)
    start(client, h)
    r = ans(client, h, "L0-1", 1).json()
    assert r["correct"] is False
    assert "solution" not in r and "explain" not in r


# ---------------------------------------------------------------- start + order of play
def test_must_accept_rules_and_start_first(client):
    h = login(client)
    assert client.post("/api/dicts/open", json={"qid": "L0-1"}, headers=h).status_code == 409
    assert client.post("/api/dicts/start", json={"accept_rules": False}, headers=h).status_code == 422
    st = start(client, h)
    assert st["remaining"] == 45 * 60 and st["levels"][0]["unlocked"] and not st["levels"][1]["unlocked"]


def test_locked_stage_is_refused(client):
    h = login(client)
    start(client, h)
    assert client.post("/api/dicts/open", json={"qid": "L1-1"}, headers=h).status_code == 403
    clear_stage(client, h, "L0")
    assert client.post("/api/dicts/open", json={"qid": "L1-1"}, headers=h).status_code == 200


# ---------------------------------------------------------------- per-question timer
def test_question_deadline_is_fixed_at_first_open(client, clock):
    h = login(client)
    start(client, h)
    r1 = client.post("/api/dicts/open", json={"qid": "L0-1"}, headers=h).json()
    assert r1["limit"] == C.QUESTIONS["L0-1"]["time"] and r1["remaining"] == r1["limit"]
    clock.t += 20
    r2 = client.post("/api/dicts/open", json={"qid": "L0-1"}, headers=h).json()
    assert r2["remaining"] == r1["limit"] - 20  # leaving and coming back does not reset it


def test_expire_too_early_then_on_time(client, clock):
    h = login(client)
    start(client, h)
    client.post("/api/dicts/open", json={"qid": "L0-1"}, headers=h)
    assert client.post("/api/dicts/expire", json={"qid": "L0-1"}, headers=h).status_code == 409
    clock.t += C.QUESTIONS["L0-1"]["time"]
    r = client.post("/api/dicts/expire", json={"qid": "L0-1"}, headers=h).json()
    assert r["state"]["questions"]["L0-1"]["timed_out"] and r["solution"]["index"] == 0 and r["explain"]
    assert r["state"]["xp"] == 0 and r["state"]["combo"] == 0


def test_late_answer_is_timed_out(client, clock):
    h = login(client)
    start(client, h)
    client.post("/api/dicts/open", json={"qid": "L0-1"}, headers=h)
    clock.t += C.QUESTIONS["L0-1"]["time"] + engine.GRACE + 1
    r = client.post("/api/dicts/answer", json={"qid": "L0-1", "answer": 0}, headers=h).json()
    assert r["timed_out"] and r["state"]["xp"] == 0 and r["solution"]


# ---------------------------------------------------------------- XP rules
def test_first_try_no_hint_gets_20_percent(client):
    h = login(client)
    start(client, h)
    r = ans(client, h, "L0-1", 0).json()
    assert r["correct"] and r["xp"] == 12 and r["xp_parts"]["clean"] == 2  # base 10 + 20%


def test_fixing_a_mistake_earns_60_percent_and_miss_keeps_xp(client):
    h = login(client)
    start(client, h)
    solve(client, h, "L0-1")
    before = client.get("/api/dicts/mission", headers=h).json()["state"]["xp"]
    r = ans(client, h, "L0-2", False).json()  # wrong
    assert not r["correct"] and r["combo"] == 0 and r["state"]["xp"] == before  # a miss never removes XP
    r = ans(client, h, "L0-2", True).json()
    assert r["correct"] and r["xp"] == 6 and r["xp_parts"]["clean"] == 0  # 60% of 10


def test_hint_costs_a_little_xp_and_unlocks_progressively(client):
    h = login(client)
    start(client, h)
    client.post("/api/dicts/open", json={"qid": "L1-6"}, headers=h)  # needs L1 unlocked
    clear_stage(client, h, "L0")
    r = client.post("/api/dicts/hint", json={"qid": "L1-6"}, headers=h).json()
    assert r["concept"] == "pairs" and len(r["hints"]) == 1 and r["more"] is True
    r = client.post("/api/dicts/hint", json={"qid": "L1-6"}, headers=h).json()
    assert len(r["hints"]) == 2 and r["more"] is False
    res = ans(client, h, "L1-6", right(C.QUESTIONS["L1-6"])).json()
    base = C.QUESTIONS["L1-6"]["xp"]  # 15: 2 hints cost 2 x 2; no first-try bonus with a hint
    assert res["correct"] and res["xp_parts"]["clean"] == 0 and res["xp_parts"]["base"] == base - 2 * max(1, round(base * 0.1))


def test_combo_bonus_from_three_in_a_row(client):
    h = login(client)
    start(client, h)
    xs = [solve(client, h, q) for q in ("L0-1", "L0-2", "L0-3")]
    assert [x["combo"] for x in xs] == [1, 2, 3]
    assert xs[2]["xp_parts"]["combo"] > 0 and xs[1]["xp_parts"]["combo"] == 0


def test_replay_gives_no_new_xp(client):
    h = login(client)
    start(client, h)
    clear_stage(client, h, "L0")
    xp = client.get("/api/dicts/mission", headers=h).json()["state"]["xp"]
    r = ans(client, h, "L0-1", 0).json()
    assert r["correct"] and r["already_solved"] and r["xp"] == 0 and r["state"]["xp"] == xp


# ---------------------------------------------------------------- reveal rule
def test_solution_unlocks_only_after_n_wrong_tries(client):
    h = login(client)
    start(client, h)
    assert client.post("/api/dicts/reveal", json={"qid": "L0-1"}, headers=h).status_code == 403
    r1 = ans(client, h, "L0-1", 1).json()
    assert r1["can_reveal"] is False
    r2 = ans(client, h, "L0-1", 2).json()
    assert r2["can_reveal"] is True
    r = client.post("/api/dicts/reveal", json={"qid": "L0-1"}, headers=h).json()
    assert r["solution"]["index"] == 0 and r["state"]["questions"]["L0-1"]["revealed"] and r["state"]["xp"] == 0


# ---------------------------------------------------------------- stars + badges + unlock
def test_three_stars_needs_every_first_try(client):
    h = login(client)
    start(client, h)
    clear_stage(client, h, "L0")
    clear_stage(client, h, "L1")
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    l0, l1 = st["levels"][0], st["levels"][1]
    assert l0["done"] and l0["stars"] == 3 and l1["stars"] == 3 and st["levels"][2]["unlocked"]
    assert "board-explorer" in st["badges"] and "clean-sweep" in st["badges"] and "combo-5" in st["badges"]


def test_stars_drop_with_mistakes(client):
    h = login(client)
    start(client, h)
    ans(client, h, "L0-1", 1)
    solve(client, h, "L0-1")
    ans(client, h, "L0-2", False)
    solve(client, h, "L0-2")
    solve(client, h, "L0-3")
    lv = client.get("/api/dicts/mission", headers=h).json()["state"]["levels"][0]
    assert lv["done"] and lv["first_try"] == 1 and lv["stars"] == 1


# ---------------------------------------------------------------- grading details
def test_board_build_checks_order(client):
    h = login(client)
    start(client, h)
    for lid in ("L0", "L1"):
        clear_stage(client, h, lid)
    # right rows, wrong order: tea was deleted and added again instead of changed in place
    r = ans(client, h, "L2-2", {"rows": [["coffee", 15], ["tea", 14], ["samosa", 15]]}).json()
    assert not r["correct"] and any("order" in c["text"] for c in r["detail"]["checks"])
    r = ans(client, h, "L2-2", {"rows": [["tea", 14], ["coffee", 15], ["samosa", 15]]}).json()
    assert r["correct"]
    bad = ans(client, h, "L2-6", {"rows": [["tea", 12], ["tea", 13]]})
    assert bad.status_code == 422  # a board cannot hold the same key twice


def test_coding_hidden_test_note_and_exact_order(client):
    h = login(client)
    start(client, h)
    for lid in ("L0", "L1", "L2", "L3", "L4"):
        clear_stage(client, h, lid)
    q = C.QUESTIONS["L5-3"]
    outs = right(q)["outputs"]
    outs[2] = {"stdout": "{'coffee': 15, 'tea': 14}\n", "error": None}  # wrong order for a repeated name
    r = ans(client, h, "L5-3", {"outputs": outs}).json()
    assert not r["correct"]
    t = r["detail"]["tests"][2]
    assert t["hidden"] and not t["passed"] and t["note"] == "a name read out twice"
    outs[2] = {"stdout": "", "error": {"type": "KeyError", "msg": "'x'"}}
    r = ans(client, h, "L5-3", {"outputs": outs}).json()
    assert r["detail"]["tests"][2]["error"] == "KeyError"


def test_optimize_challenge_rejects_two_lists(client):
    h = login(client)
    start(client, h)
    for lid in ("L0", "L1", "L2", "L3", "L4", "L5"):
        clear_stage(client, h, lid)
    for qid in ("B-1", "B-2", "B-3"):
        solve(client, h, qid)
    q = C.QUESTIONS["B-4"]
    r = ans(client, h, "B-4", right(q), code=q["challenge"]["starter"]).json()
    assert not r["correct"] and "Every test passes" in r["detail"]["why_wrong"]
    r = ans(client, h, "B-4", right(q), code=q["solution"]).json()
    assert r["correct"]


def test_malformed_answer_is_422(client):
    h = login(client)
    start(client, h)
    assert ans(client, h, "L0-1", "zero").status_code == 422
    assert ans(client, h, "L0-2", 1).status_code == 422


# ---------------------------------------------------------------- mission clock + proctoring
def test_mission_clock_ends_the_mission(client, clock):
    h = login(client)
    start(client, h)
    clock.t += 45 * 60 + 1
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_reason"] == "time" and st["remaining"] == 0
    r = client.post("/api/dicts/open", json={"qid": "L0-1"}, headers=h)
    assert r.status_code == 409 and r.json()["detail"] == "mission-over"


def test_remaining_time_is_not_rounded_down(client, clock):
    # The browser counts down from `remaining`; rounding down would make it end the mission early,
    # find the server still running, and show "Mission in progress" on the report.
    h = login(client)
    start(client, h)
    clock.t += 0.4
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["remaining"] == pytest.approx(45 * 60 - 0.4)


def test_tab_switch_limit_ends_mission(client):
    h = login(client)
    start(client, h)
    for i in range(1, 3):
        r = client.post("/api/dicts/proctor", json={"type": "tab_switch", "duration_ms": 4000}, headers=h).json()
        assert r["counted"] and not r["ended"] and r["tab_switches"] == i
    r = client.post("/api/dicts/proctor", json={"type": "tab_switch", "duration_ms": 4000}, headers=h).json()
    assert r["ended"] and r["state"]["ended_reason"] == "proctor"
    assert ans(client, h, "L0-1", 0, open_first=False).json()["detail"] == "mission-over"


def test_copy_paste_and_second_tab_are_recorded(client):
    h = login(client)
    start(client, h)
    for t in ("copy", "paste", "contextmenu"):
        client.post("/api/dicts/proctor", json={"type": t}, headers=h)
    client.post("/api/dicts/proctor", json={"type": "multi_tab"}, headers=h)
    assert client.post("/api/dicts/proctor", json={"type": "bogus"}, headers=h).status_code == 422
    t = teacher(client)
    row = client.get("/api/teacher/dicts", headers=t).json()["students"][0]
    assert row["copy_paste"] == 3 and row["multi_tab"] == 1


# ---------------------------------------------------------------- teacher dashboard
def test_teacher_dashboard_columns_and_current_question(client):
    t = teacher(client)
    assert client.post("/api/teacher/login", json={"password": "nope"}).status_code == 401
    assert client.get("/api/teacher/dicts").status_code == 401
    h = login(client, name="Anu")
    start(client, h)
    solve(client, h, "L0-1")
    client.post("/api/dicts/open", json={"qid": "L0-2"}, headers=h)
    d = client.get("/api/teacher/dicts", headers=t).json()
    o = d["overview"]
    assert o["students"] == 1 and o["started"] == 1 and o["online"] == 1 and o["accuracy"] == 1.0
    s = d["students"][0]
    for k in ("rank", "name", "roll_no", "section", "status", "status_label", "done", "total", "first_try", "timed_out",
              "revealed", "used_minutes", "tab_switches", "copy_paste", "concepts", "last_seen", "online", "current"):
        assert k in s, k
    assert s["current"]["qid"] == "L0-2" and s["current"]["stage"] == "Mission Briefing" and s["current"]["n"] == 2
    assert [x["name"] for x in d["stages"]][0] == "Mission Briefing" and d["total_questions"] == 42


def test_section_filter(client):
    t = teacher(client)
    login(client, name="A1", section="Section A")
    login(client, name="B1", section="Section B")
    d = client.get("/api/teacher/dicts?section=Section%20B", headers=t).json()
    assert [s["name"] for s in d["students"]] == ["B1"]


def test_reset_and_delete(client):
    t = teacher(client)
    h = login(client)
    start(client, h)
    solve(client, h, "L0-1")
    sid = client.get("/api/me", headers=h).json()["student"]["id"]
    assert client.post(f"/api/teacher/dicts/{sid}/reset", headers=t).status_code == 200
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["xp"] == 0 and st["started_at"] is None  # fresh attempt, still signed in
    assert client.delete(f"/api/teacher/students/{sid}", headers=t).status_code == 200
    assert client.get("/api/me", headers=h).status_code == 401
    assert client.delete(f"/api/teacher/students/{sid}", headers=t).status_code == 404


def test_csv_export(client):
    t = teacher(client)
    h = login(client, name="Teja, R")
    start(client, h)
    solve(client, h, "L0-1")
    r = client.get("/api/teacher/dicts/export.csv", headers=t)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    lines = r.text.strip().splitlines()
    assert lines[0].startswith("rank,name,roll_no,section,status,xp") and '"Teja, R"' in lines[1]


def test_leaderboard_is_per_section(client):
    h1 = login(client, name="Top", section="Section A")
    h2 = login(client, name="Second", section="Section A")
    login(client, name="Other", section="Section C")
    start(client, h1)
    start(client, h2)
    solve(client, h1, "L0-1")
    lb = client.get("/api/dicts/leaderboard", headers=h2).json()
    assert [r["name"] for r in lb["rows"]] == ["Top", "Second"] and lb["me"]["rank"] == 2 and lb["count"] == 2


# ---------------------------------------------------------------- teacher resume + idle / offline
def end_by_tab_switches(client, h):
    for _ in range(3):
        r = client.post("/api/dicts/proctor", json={"type": "tab_switch", "duration_ms": 2000}, headers=h).json()
    assert r["state"]["ended_reason"] == "proctor"


def sid_of(client, h):
    return client.get("/api/me", headers=h).json()["student"]["id"]


def test_resume_after_tab_switches_keeps_progress_and_time(client, clock):
    t = teacher(client)
    h = login(client)
    start(client, h)
    solve(client, h, "L0-1")
    clock.t += 600                                   # 10 minutes used
    client.post("/api/dicts/open", json={"qid": "L0-2"}, headers=h)
    clock.t += 10                                    # 10 of L0-2's 30 seconds used
    end_by_tab_switches(client, h)
    xp = client.get("/api/dicts/mission", headers=h).json()["state"]["xp"]
    clock.t += 1800                                  # the teacher notices 30 minutes later
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_reason"] == "proctor"           # still ended: those 30 minutes are not the clock running out
    r = client.post(f"/api/teacher/dicts/{sid_of(client, h)}/resume", headers=t)
    assert r.status_code == 200
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_at"] is None and st["xp"] == xp and st["questions"]["L0-1"]["solved"]
    assert st["remaining"] == pytest.approx(45 * 60 - 610)           # exactly the time that was left
    assert st["proctor"]["tab_switches"] == 0                         # a fresh allowance of 3
    o = client.post("/api/dicts/open", json={"qid": "L0-2"}, headers=h).json()
    assert o["remaining"] == pytest.approx(C.QUESTIONS["L0-2"]["time"] - 10)  # the open question keeps its seconds
    assert solve(client, h, "L0-2")["correct"]
    row = client.get("/api/teacher/dicts", headers=t).json()["students"][0]
    assert row["tab_switches"] == 3 and row["resumes"] == 1 and row["status"] == "in progress"


def test_resume_after_time_gives_at_least_five_minutes(client, clock):
    t = teacher(client)
    h = login(client)
    start(client, h)
    clock.t += 45 * 60 + 5
    assert client.get("/api/dicts/mission", headers=h).json()["state"]["ended_reason"] == "time"
    client.post(f"/api/teacher/dicts/{sid_of(client, h)}/resume", headers=t)
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_at"] is None and st["remaining"] == pytest.approx(300)
    clock.t += 301
    assert client.get("/api/dicts/mission", headers=h).json()["state"]["ended_reason"] == "time"


def test_resume_refused_when_not_ended_or_complete(client):
    t = teacher(client)
    h = login(client)
    sid = sid_of(client, h)
    assert client.post(f"/api/teacher/dicts/{sid}/resume", headers=t).status_code == 409   # not started
    start(client, h)
    assert client.post(f"/api/teacher/dicts/{sid}/resume", headers=t).status_code == 409   # running
    for l in C.LEVELS:
        clear_stage(client, h, l["id"])
    assert client.post(f"/api/teacher/dicts/{sid}/resume", headers=t).status_code == 409   # completed
    assert client.post("/api/teacher/dicts/999/resume", headers=t).status_code == 404
    assert client.post(f"/api/teacher/dicts/{sid}/resume").status_code == 401             # teacher only


def test_resume_works_on_a_state_saved_before_this_feature(client, clock):
    t = teacher(client)
    h = login(client)
    start(client, h)
    end_by_tab_switches(client, h)
    sid = sid_of(client, h)
    old = db.by_id(sid)["state"]
    for k in ("paused", "grace", "resumes", "last_action"):
        old.pop(k)
    old["proctor"].pop("tab_total")
    db.save_state(sid, old)
    assert client.post(f"/api/teacher/dicts/{sid}/resume", headers=t).status_code == 200
    assert client.get("/api/dicts/mission", headers=h).json()["state"]["ended_at"] is None


def test_idle_and_offline_are_shown_to_the_teacher(client, clock):
    t = teacher(client)
    h = login(client)
    start(client, h)
    row = lambda: client.get("/api/teacher/dicts", headers=t).json()["students"][0]  # noqa: E731
    assert row()["activity"] == "active"
    clock.t += 60
    client.post("/api/ping", headers=h)                 # page open, heartbeat only
    clock.t += 65
    client.post("/api/ping", headers=h)
    r = row()
    assert r["activity"] == "idle" and r["idle_seconds"] >= 120
    assert client.get("/api/teacher/dicts", headers=t).json()["overview"]["attention"] == 1
    client.post("/api/dicts/open", json={"qid": "L0-1"}, headers=h)   # a real step clears it
    assert row()["activity"] == "active"
    clock.t += main.ONLINE_WINDOW + 1                     # page closed: no heartbeat
    assert row()["activity"] == "offline"
    end_by_tab_switches(client, h)
    r = row()
    assert r["activity"] is None and r["can_resume"] and r["current"]["qid"] == "L0-1"  # shows where they stopped


def test_teacher_resume_does_not_mark_student_online(client, clock):
    t = teacher(client)
    h = login(client)
    start(client, h)
    sid = sid_of(client, h)  # read before the clock moves: /api/me is the student's own call and counts as "seen"
    end_by_tab_switches(client, h)
    clock.t += main.ONLINE_WINDOW + 5
    client.post(f"/api/teacher/dicts/{sid}/resume", headers=t)
    r = client.get("/api/teacher/dicts", headers=t).json()["students"][0]
    assert r["online"] is False and r["activity"] == "offline"


def test_scripts_are_never_stale_and_dashboard_knows_the_build(client):
    # an open dashboard compares `build` and reloads itself after a server update
    t = teacher(client)
    assert client.get("/api/teacher/dicts", headers=t).json()["build"] == main.BUILD
    for path in ("/static/js/teacher.js", "/static/js/dicts.js", "/static/css/teacher.css"):
        assert client.get(path).headers["cache-control"] == "no-cache", path


# ---------------------------------------------------------------- full mission
def test_full_mission_complete(client):
    h = login(client)
    start(client, h)
    for l in C.LEVELS:
        clear_stage(client, h, l["id"])
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_reason"] == "complete" and st["progress"] == {"done": 42, "total": 42}
    assert set(st["badges"]) == set(C.BADGES), set(C.BADGES) - set(st["badges"])
    assert all(l["stars"] == 3 for l in st["levels"])
    rev = client.get("/api/dicts/review", headers=h).json()
    assert rev["items"] == []
