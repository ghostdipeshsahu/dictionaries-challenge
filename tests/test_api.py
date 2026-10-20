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


TEST_PG = os.environ.get("TEST_DATABASE_URL")  # run the same suite against Postgres (see tests/run_pg.py)


@pytest.fixture()
def client(clock):
    if TEST_PG:
        db.connect(TEST_PG)
        db._run("TRUNCATE students, events, teacher_tokens RESTART IDENTITY")
    else:
        db.connect(":memory:")
    main.TEACHER_PASSWORD = "test-pass"
    return TestClient(main.app)


S29, S30 = C.MISSION == "s29", C.MISSION == "s30"
only_s29 = pytest.mark.skipif(not S29, reason="Session 29 question")
only_s30 = pytest.mark.skipif(not S30, reason="Session 30 question")

MISSION_S = main.RULES.mission_seconds  # the mission's own clock (40 min for Session 29, 45 for Session 30)

_roll = [0]


def login(client, name="Ravi Kumar", section="Section A", roll=None):
    _roll[0] += 1
    r = client.post("/api/login", json={"name": name, "roll_no": roll or f"R{_roll[0]:03d}", "section": section,
                                          "university": "NIAT Hyderabad", "contact": "9876543210"})
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
    if t == "land":
        return q["mapping"]
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
def test_health(client):
    r = client.get("/api/health").json()
    assert r["ok"] and r["class_code_required"] is False and "sections" not in r


def test_login_validation(client):
    ok = {"name": "A", "roll_no": "1", "section": "S-001", "university": "NIAT", "contact": "9876543210"}
    for bad in ({"section": ""}, {"section": " - "}, {"university": ""}, {"university": "X"}, {"contact": ""},
                {"contact": "12345"}, {"contact": "5876543210"}):
        assert client.post("/api/login", json=dict(ok, **bad)).status_code == 422, bad


def test_students_type_their_section_and_university(client):
    """No fixed list: any section is accepted, and "s 001" joins the "S-001" already in use."""
    h1 = client.post("/api/login", json={"name": "A", "roll_no": "1", "section": "s-001", "university": " NIAT  Hyd ", "contact": "9876543210"}).json()
    assert h1["student"]["section"] == "S-001" and h1["student"]["university"] == "NIAT Hyd"
    h2 = client.post("/api/login", json={"name": "B", "roll_no": "2", "section": "S 001", "university": "NIAT", "contact": "9876543210"}).json()
    assert h2["student"]["section"] == "S-001"
    h3 = client.post("/api/login", json={"name": "C", "roll_no": "3", "section": "CSE B", "university": "NIAT", "contact": "9876543210"}).json()
    assert h3["student"]["section"] == "CSE B"
    # signing in again with the section typed another way is the same student
    assert client.post("/api/login", json={"name": "A", "roll_no": "1", "section": "S001", "university": "NIAT", "contact": "9876543210"}).status_code in (200, 409)
    d = client.get("/api/teacher/dicts", headers=teacher(client)).json()
    assert d["sections"] == ["CSE B", "S-001"]
    assert {s["name"]: s["university"] for s in d["students"]} == {"A": "NIAT Hyd", "B": "NIAT", "C": "NIAT"}
    assert {s["contact"] for s in d["students"]} == {"9876543210"}
    r = client.post("/api/login", json={"name": "D", "roll_no": "4", "section": "S-001", "university": "NIAT", "contact": "+91 91234-56789"})
    assert r.status_code == 200
    assert [s["contact"] for s in client.get("/api/teacher/dicts", headers=teacher(client)).json()["students"] if s["name"] == "D"] == ["9123456789"]
    assert client.post("/api/login", json={"name": " ", "roll_no": "1", "section": "Section A", "university": "NIAT", "contact": "9876543210"}).status_code == 422


def test_one_device_at_a_time_and_release(client, clock):
    h1 = login(client, roll="X1")
    r = client.post("/api/login", json={"name": "Ravi Kumar", "roll_no": "x1", "section": "Section A", "university": "NIAT", "contact": "9876543210"})
    assert r.status_code == 409 and "another device" in r.json()["detail"]
    # same roll number, different name: refused
    assert client.post("/api/login", json={"name": "Someone", "roll_no": "X1", "section": "Section A", "university": "NIAT", "contact": "9876543210"}).status_code == 409
    # teacher releases the login: old device is signed out, a new device can sign in
    sid = client.get("/api/me", headers=h1).json()["student"]["id"]
    t = teacher(client)
    assert client.post(f"/api/teacher/students/{sid}/release", headers=t).status_code == 200
    assert client.post("/api/ping", headers=h1).status_code == 401
    assert client.post("/api/login", json={"name": "ravi kumar", "roll_no": "X1", "section": "Section A", "university": "NIAT", "contact": "9876543210"}).status_code == 200


def test_device_lock_expires_without_heartbeat(client, clock):
    login(client, roll="X2")
    clock.t += main.DEVICE_LOCK + 1
    assert client.post("/api/login", json={"name": "Ravi Kumar", "roll_no": "X2", "section": "Section A", "university": "NIAT", "contact": "9876543210"}).status_code == 200


def test_logout(client):
    h = login(client)
    assert client.post("/api/logout", headers=h).status_code == 200
    assert client.get("/api/me", headers=h).status_code == 401


# ---------------------------------------------------------------- answer keys never leak
SECRET_KEYS = {"answer", "answers", "value", "blanks", "mapping", "line", "error", "target", "why", "solution", "rules", "hints", "explain", "trap"}


def test_mission_payload_has_no_answer_keys(client):
    h = login(client)
    m = client.get("/api/dicts/mission", headers=h).json()
    assert len(m["levels"]) == len(C.LEVELS) and sum(len(l["questions"]) for l in m["levels"] if not l.get("bonus")) == C.TOTAL
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
    assert st["remaining"] == MISSION_S and st["levels"][0]["unlocked"] and not st["levels"][1]["unlocked"]


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
    hq = next(q for l in C.LEVELS[1:] for q in l["main"] if len(C.QUESTIONS[q]["hints"]) >= 2)
    assert client.post("/api/dicts/open", json={"qid": hq}, headers=h).status_code == 403  # its stage is still locked
    for l in C.LEVELS[:C.LEVEL_IDS.index(C.QUESTIONS[hq]["stage"])]:
        clear_stage(client, h, l["id"])
    r = client.post("/api/dicts/hint", json={"qid": hq}, headers=h).json()
    assert r["concept"] == C.QUESTIONS[hq]["concept"] and len(r["hints"]) == 1 and r["more"] is True
    r = client.post("/api/dicts/hint", json={"qid": hq}, headers=h).json()
    assert len(r["hints"]) == 2 and r["more"] is False
    res = ans(client, h, hq, right(C.QUESTIONS[hq])).json()
    base = C.QUESTIONS[hq]["xp"]  # 2 hints cost 2 x 10% of base; no first-try bonus with a hint
    assert res["correct"] and res["xp_parts"]["clean"] == 0 and res["xp_parts"]["base"] == base - 2 * max(1, round(base * 0.1))


def test_combo_bonus_from_three_in_a_row(client):
    h = login(client)
    start(client, h)
    xs = [solve(client, h, q) for q in [q for l in C.LEVELS for q in l["main"]][:3]]
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
    assert C.STAGE_BADGE["L1"] in st["badges"] and "clean-sweep" in st["badges"] and "combo-5" in st["badges"]


def test_stars_drop_with_mistakes(client):
    h = login(client)
    start(client, h)
    ans(client, h, "L0-1", 1)
    solve(client, h, "L0-1")
    ans(client, h, "L0-2", False)
    solve(client, h, "L0-2")
    for q in C.LEVEL_BY_ID["L0"]["main"][2:]:
        solve(client, h, q)
    lv = client.get("/api/dicts/mission", headers=h).json()["state"]["levels"][0]
    assert lv["done"] and lv["first_try"] == len(C.LEVEL_BY_ID["L0"]["main"]) - 2 and lv["stars"] == 1


# ---------------------------------------------------------------- grading details
@only_s29
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
    qid = next(q["id"] for l in C.LEVELS for q in (C.QUESTIONS[x] for x in l["main"])
               if q["type"] == "coding" and any(t.get("hidden") and t.get("note") for t in q["challenge"]["tests"]))
    for l in C.LEVELS[:C.LEVEL_IDS.index(C.QUESTIONS[qid]["stage"])]:
        clear_stage(client, h, l["id"])
    q = C.QUESTIONS[qid]
    i = next(k for k, t in enumerate(q["challenge"]["tests"]) if t.get("hidden") and t.get("note"))
    outs = right(q)["outputs"]
    outs[i] = {"stdout": "something else\n", "error": None}  # one hidden test fails
    r = ans(client, h, qid, {"outputs": outs}, code=q["solution"]).json()
    assert not r["correct"]
    t = r["detail"]["tests"][i]
    assert t["hidden"] and not t["passed"] and t["note"] == q["challenge"]["tests"][i]["note"]
    outs[i] = {"stdout": "", "error": {"type": "KeyError", "msg": "'x'"}}
    r = ans(client, h, qid, {"outputs": outs}, code=q["solution"]).json()
    assert r["detail"]["tests"][i]["error"] == "KeyError"


@only_s29
def test_optimize_challenge_rejects_two_lists(client):
    h = login(client)
    start(client, h)
    for lid in ("L0", "L1", "L2", "L3", "L4", "L5"):
        clear_stage(client, h, lid)
    for qid in ("B-1",):
        solve(client, h, qid)
    q = C.QUESTIONS["B-4"]
    r = ans(client, h, "B-4", right(q), code=q["challenge"]["starter"]).json()
    assert not r["correct"] and "Every test passes" in r["detail"]["why_wrong"]
    r = ans(client, h, "B-4", right(q), code=q["solution"]).json()
    assert r["correct"]


@only_s30
def test_split_the_bill_must_use_star_friends(client):
    # equal output is not enough: the starter's three-parameter split() is refused by the code check
    h = login(client)
    start(client, h)
    for lid in ("L0", "L1", "L2", "L3", "L4"):
        clear_stage(client, h, lid)
    clear_stage(client, h, "L5")
    q = C.QUESTIONS["B-5"]  # One Split for All: split3/split4 give the right output for 3 and 4 friends
    r = ans(client, h, "B-5", right(q), code=q["challenge"]["starter"]).json()
    assert not r["correct"] and "Every test passes" in r["detail"]["why_wrong"] and "split(bill, *friends)" in r["detail"]["why_wrong"]
    assert ans(client, h, "B-5", right(q), code=q["solution"]).json()["correct"]


@only_s30
def test_landing_question_is_graded_per_argument(client):
    h = login(client)
    start(client, h)
    for lid in ("L0", "L1", "L2", "L3"):
        clear_stage(client, h, lid)
    for qid in ("L4-1", "L4-4"):
        solve(client, h, qid)
    q = C.QUESTIONS["L4-6"]
    nobox = len(q["boxes"])  # one past the last box means "no box"
    wrong = list(q["mapping"])
    wrong[0] = next(b for b in range(nobox + 1) if b != wrong[0])  # first argument in the wrong place
    per = [w == m for w, m in zip(wrong, q["mapping"])]
    r = ans(client, h, "L4-6", wrong).json()
    assert not r["correct"] and r["detail"]["per_item"] == per and r["detail"]["right_count"] == sum(per)
    assert "solution" not in r
    assert ans(client, h, "L4-6", wrong[:-1] + [nobox + 1]).status_code == 422  # not a box
    assert ans(client, h, "L4-6", wrong[:-1]).status_code == 422                # one argument left unplaced
    r = ans(client, h, "L4-6", q["mapping"]).json()
    assert r["correct"]


@only_s30
def test_landing_no_box_and_reveal_gives_the_printed_line(client):
    h = login(client)
    start(client, h)
    for lid in ("L0", "L1", "L2", "L3"):
        clear_stage(client, h, lid)
    for qid in ("L4-1", "L4-4"):
        solve(client, h, qid)
    nobox = len(C.QUESTIONS["L4-6"]["boxes"])
    ans(client, h, "L4-6", [0, 0])
    ans(client, h, "L4-6", [0, nobox])
    r = client.post("/api/dicts/reveal", json={"qid": "L4-6"}, headers=h).json()
    assert r["solution"]["mapping"] == [nobox, nobox] and r["solution"]["text"].startswith("!TypeError")


def test_malformed_answer_is_422(client):
    h = login(client)
    start(client, h)
    assert ans(client, h, "L0-1", "zero").status_code == 422
    assert ans(client, h, "L0-2", 1).status_code == 422


# ---------------------------------------------------------------- mission clock + proctoring
def test_mission_clock_ends_the_mission(client, clock):
    h = login(client)
    start(client, h)
    clock.t += MISSION_S + 1
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
    assert st["remaining"] == pytest.approx(MISSION_S - 0.4)


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
    assert s["current"]["qid"] == "L0-2" and s["current"]["stage"] == C.LEVELS[0]["name"] and s["current"]["n"] == 2
    assert [x["name"] for x in d["stages"]][0] == C.LEVELS[0]["name"] and d["total_questions"] == C.TOTAL


def test_section_filter(client):
    t = teacher(client)
    login(client, name="A1", section="Section A")
    login(client, name="B1", section="Section B")
    d = client.get("/api/teacher/dicts?section=SECTION%20B", headers=t).json()
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
    lines = r.text.lstrip("\ufeff").strip().splitlines()
    assert lines[0].startswith("rank,name,roll_no,section,university,contact,status,xp") and '"Teja, R"' in lines[1]


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
    assert st["remaining"] == pytest.approx(MISSION_S - 610)           # exactly the time that was left
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
    clock.t += MISSION_S + 5
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


def test_simultaneous_answers_are_counted_once(client):
    # A double-clicked Check, or two servers handling the same student at once (Vercel), must not award XP
    # twice: each change runs in a transaction that locks the student's row.
    import concurrent.futures
    h = login(client)
    start(client, h)
    client.post("/api/dicts/open", json={"qid": "L0-1"}, headers=h)
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda _: client.post("/api/dicts/answer", json={"qid": "L0-1", "answer": 0}, headers=h).json(), range(8)))
    assert sum(1 for r in results if r["correct"] and not r.get("already_solved")) == 1
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["xp"] == 12 and st["combo"] == 1


HAS_BONUS = any(l.get("bonus") for l in C.LEVELS)
only_bonus = pytest.mark.skipif(not HAS_BONUS, reason="this mission has no bonus round")


def clear_core(client, h):
    for l in C.LEVELS:
        if not l.get("bonus"):
            clear_stage(client, h, l["id"])


@only_bonus
def test_bonus_round_opens_after_the_boss_and_mission_counts_as_complete(client):
    t = teacher(client)
    h = login(client)
    start(client, h)
    assert client.post("/api/dicts/finish", headers=h).status_code == 409   # not before the Final Boss
    clear_core(client, h)
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_at"] is None and st["core_done"] and st["progress"] == {"done": C.TOTAL, "total": C.TOTAL}
    assert st["levels"][-1]["unlocked"] and not st["levels"][-1]["done"]
    row = client.get("/api/teacher/dicts", headers=t).json()["students"][0]
    assert row["status"] == "complete" and row["done"] == C.TOTAL and not row["can_resume"]
    first_bonus = next(l for l in C.LEVELS if l.get("bonus"))["main"][0]
    assert solve(client, h, first_bonus)["xp"] > 0   # bonus XP counts


@only_bonus
def test_finish_skips_the_bonus_round(client):
    h = login(client)
    start(client, h)
    clear_core(client, h)
    st = client.post("/api/dicts/finish", headers=h).json()["state"]
    assert st["ended_reason"] == "complete"
    assert client.post("/api/dicts/open", json={"qid": next(l for l in C.LEVELS if l.get("bonus"))["main"][0]}, headers=h).json()["detail"] == "mission-over"


@only_bonus
def test_clock_or_tab_switches_during_the_bonus_still_count_as_complete(client, clock):
    h = login(client)
    start(client, h)
    clear_core(client, h)
    for _ in range(3):
        r = client.post("/api/dicts/proctor", json={"type": "tab_switch", "duration_ms": 2000}, headers=h).json()
    assert r["state"]["ended_reason"] == "complete"
    h2 = login(client, name="Second")
    start(client, h2)
    clear_core(client, h2)
    clock.t += MISSION_S + 1
    assert client.get("/api/dicts/mission", headers=h2).json()["state"]["ended_reason"] == "complete"


@only_bonus
def test_clearing_the_bonus_ends_the_mission_with_its_badge(client):
    h = login(client)
    start(client, h)
    clear_core(client, h)
    for l in C.LEVELS:
        if l.get("bonus"):
            clear_stage(client, h, l["id"])
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_reason"] == "complete" and C.STAGE_BADGE["BONUS"] in st["badges"]


def test_progress_on_a_removed_question_still_loads(client):
    # A question removed from the mission after students answered it must not break their page or the dashboard.
    t = teacher(client)
    h = login(client)
    start(client, h)
    solve(client, h, "L0-1")
    sid = sid_of(client, h)
    st = db.by_id(sid)["state"]
    st["q"]["ZZ-9"] = dict(st["q"]["L0-1"])
    st["current"] = "ZZ-9"
    db.save_state(sid, st)
    m = client.get("/api/dicts/mission", headers=h)
    assert m.status_code == 200 and "ZZ-9" not in m.json()["state"]["questions"]
    d = client.get("/api/teacher/dicts", headers=t)
    assert d.status_code == 200 and d.json()["students"][0]["current"] is None
    assert client.get("/api/dicts/review", headers=h).status_code == 200


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
    assert st["ended_reason"] == "complete" and st["progress"] == {"done": C.TOTAL, "total": C.TOTAL}
    assert set(st["badges"]) == set(C.BADGES), set(C.BADGES) - set(st["badges"])
    assert all(l["stars"] == 3 for l in st["levels"])
    rev = client.get("/api/dicts/review", headers=h).json()
    assert rev["items"] == []


# ---------- end-of-mission feedback ----------
FB = {"enjoy": 5, "toughest": C.LEVELS[2]["id"], "favourite": "BOSS", "difficulty": "right", "pace": "more",
      "confidence": 4, "helped": ["predict", "coding", "made-up"], "tech": "small", "improve": "More coding time"}


def test_feedback_opens_only_after_the_mission_ends(client, clock):
    h = login(client)
    start(client, h)
    r = client.post("/api/dicts/feedback", json=FB, headers=h)
    assert r.status_code == 409
    clock.t += MISSION_S + 1
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_reason"] == "time" and st["feedback_done"] is False
    r = client.post("/api/dicts/feedback", json=FB, headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["state"]["feedback_done"] is True
    # a repeat send (a retry) changes nothing
    r = client.post("/api/dicts/feedback", json=dict(FB, enjoy=1), headers=h)
    assert r.status_code == 200 and r.json()["already"] is True


def test_tab_switch_stop_waits_for_the_teacher_not_the_feedback(client, clock):
    """Three tab switches pause the mission: the student is asked to get the teacher to resume it. Feedback opens
    only when the mission is over for good: every stage cleared, or the clock ran out with no resume."""
    h = login(client)
    start(client, h)
    end_by_tab_switches(client, h)
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_reason"] == "proctor" and st["feedback_open"] is False
    r = client.post("/api/dicts/feedback", json=FB, headers=h)
    assert r.status_code == 409 and "instructor" in r.json()["detail"]
    # the teacher resumes: the mission runs again, still no feedback
    t = teacher(client)
    assert client.post(f"/api/teacher/dicts/{sid_of(client, h)}/resume", headers=t).status_code == 200
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_at"] is None and st["feedback_open"] is False
    # paused again, and this time nobody resumes before the clock is over: now the feedback opens
    end_by_tab_switches(client, h)
    clock.t += MISSION_S / 2
    assert client.get("/api/dicts/mission", headers=h).json()["state"]["feedback_open"] is False
    clock.t += MISSION_S
    assert client.get("/api/dicts/mission", headers=h).json()["state"]["feedback_open"] is True
    assert client.post("/api/dicts/feedback", json=FB, headers=h).status_code == 200


@pytest.mark.parametrize("bad", [
    {"enjoy": 0}, {"enjoy": 6}, {"confidence": None}, {"toughest": ""}, {"toughest": "BONUS"}, {"favourite": "L99"},
    {"difficulty": "meh"}, {"pace": ""}, {"tech": ""}, {"helped": ["nope"]},
])
def test_feedback_is_validated(client, clock, bad):
    h = login(client)
    start(client, h)
    clock.t += MISSION_S + 1
    r = client.post("/api/dicts/feedback", json=dict(FB, **bad), headers=h)
    assert r.status_code == 422, (bad, r.text)
    assert client.get("/api/dicts/mission", headers=h).json()["state"]["feedback_done"] is False


def test_feedback_reaches_the_teacher_dashboard_and_csv(client, clock):
    h = login(client, name="Asha Rao")
    h2 = login(client, name="Not Done Yet")
    start(client, h)
    start(client, h2)
    end_by_tab_switches(client, h)
    end_by_tab_switches(client, h2)
    clock.t += MISSION_S + 1   # nobody resumed them and the clock ran out: feedback opens
    assert client.post("/api/dicts/feedback", json=FB, headers=h).status_code == 200
    t = teacher(client)
    d = client.get("/api/teacher/dicts", headers=t).json()
    f = d["feedback"]
    assert f["count"] == 1 and f["ended"] == 2 and f["pending"] == 1
    assert f["enjoy"] == 5 and f["confidence"] == 4 and f["needed_more_time"] == 1
    assert {x["key"]: x["count"] for x in f["toughest"]}[C.LEVELS[2]["id"]] == 1
    assert {x["key"]: x["count"] for x in f["favourite"]}["BOSS"] == 1
    r = f["responses"][0]
    # who sent it comes from the sign-in
    assert r["name"] == "Asha Rao" and r["contact"] == "9876543210" and r["university"] == "NIAT Hyderabad"
    assert r["toughest_label"] == C.LEVELS[2]["name"] and r["pace_label"] == "Needed more time"
    assert r["difficulty_label"] == "Just right" and r["tech_label"] == "Yes, small ones" and len(r["helped"]) == 2
    assert r["reached"].startswith("0/") and r["status_label"] == "Paused: tab switches"
    assert {s["name"]: s["feedback_sent"] for s in d["students"]} == {"Asha Rao": True, "Not Done Yet": False}
    csv_text = client.get("/api/teacher/dicts/feedback.csv", headers=t).text
    assert "Asha Rao" in csv_text and "More coding time" in csv_text and "Not Done Yet" not in csv_text
    # the main export carries the feedback too, on each student's row
    rows = {line.split(",")[1]: line for line in client.get("/api/teacher/dicts/export.csv", headers=t).text.lstrip("\ufeff").splitlines()[1:]}
    assert "More coding time" in rows["Asha Rao"] and ",yes," in rows["Asha Rao"] and ",no," in rows["Not Done Yet"]
    # the mission payload lists this mission's "what helped" options
    m = client.get("/api/dicts/mission", headers=h).json()
    assert [x["key"] for x in m["feedback"]["helped"]] == [k for k, _, _ in C.FEEDBACK_HELPED]


def test_feedback_survives_a_resume_and_reset_clears_it(client, clock):
    h = login(client)
    start(client, h)
    end_by_tab_switches(client, h)
    clock.t += MISSION_S + 1
    assert client.post("/api/dicts/feedback", json=FB, headers=h).status_code == 200
    t = teacher(client)
    sid = sid_of(client, h)
    assert client.post(f"/api/teacher/dicts/{sid}/resume", headers=t).status_code == 200
    st = client.get("/api/dicts/mission", headers=h).json()["state"]
    assert st["ended_at"] is None and st["feedback_done"] is True   # not asked a second time
    assert client.post(f"/api/teacher/dicts/{sid}/reset", headers=t).status_code == 200
    assert client.get("/api/dicts/mission", headers=h).json()["state"]["feedback_done"] is False


def test_section_spellings_are_one_section(client):
    """The Session 29 class typed both "S-01" and "S-001": that is one section on the dashboard and the leaderboard."""
    body = {"university": "NIAT", "contact": "9876543210"}
    for i, sec in enumerate(["S-01", "S-01", "S-001", "s 1"]):
        assert client.post("/api/login", json=dict(body, name=f"Stu {i}", roll_no=f"SEC{i}", section=sec)).status_code == 200
    t = teacher(client)
    d = client.get("/api/teacher/dicts", headers=t).json()
    assert d["sections"] == ["S-01"]                                  # the spelling most students typed
    assert {s["section"] for s in d["students"]} == {"S-01"}
    assert len(client.get("/api/teacher/dicts?section=S-001", headers=t).json()["students"]) == 4


def test_correct_leaves_out_timed_out_questions(client, clock):
    h = login(client)
    start(client, h)
    solve(client, h, "L0-1")
    client.post("/api/dicts/open", json={"qid": "L0-2"}, headers=h)
    clock.t += C.QUESTIONS["L0-2"]["time"] + 1
    client.post("/api/dicts/expire", json={"qid": "L0-2"}, headers=h)
    t = teacher(client)
    row = client.get("/api/teacher/dicts", headers=t).json()["students"][0]
    assert row["done"] == 2 and row["correct"] == 1 and row["timed_out"] == 1
    lines = client.get("/api/teacher/dicts/export.csv", headers=t).text.lstrip("\ufeff").splitlines()
    head, first = lines[0].split(","), lines[1].split(",")
    assert first[head.index("got_through")] == "2" and first[head.index("correct")] == "1"


# ---------- one server, many missions ----------
OTHER = next((k for k in C.KEYS if k != C.MISSION), None)
needs_two = pytest.mark.skipif(OTHER is None, reason="this server runs one mission")
WHO = {"name": "Asha Rao", "roll_no": "MULTI1", "section": "S-001", "university": "NIAT", "contact": "9876543210"}


@needs_two
def test_each_mission_has_its_own_url_and_students(client):
    other = C.slug(OTHER)
    assert client.get("/api/health").json()["mission"] == C.MISSION
    assert client.get(f"/{other}/api/health").json()["mission"] == OTHER
    assert client.get(f"/{OTHER}/api/health").json()["mission"] == OTHER          # the key works too
    assert {m["key"] for m in client.get("/api/health").json()["missions"]} == set(C.KEYS)
    for path in (f"/{other}", f"/{other}/", f"/{other}/teacher"):
        assert client.get(path).status_code == 200
    # the same roll number signs in to both missions as two separate students
    here = client.post("/api/login", json=WHO).json()
    there = client.post(f"/{other}/api/login", json=WHO).json()
    assert here["student"]["id"] != there["student"]["id"]
    h_here, h_there = ({"Authorization": "Bearer " + x["token"]} for x in (here, there))
    # a sign-in opens only its own mission
    assert client.get(f"/{other}/api/dicts/mission", headers=h_here).status_code == 401
    assert client.get("/api/dicts/mission", headers=h_there).status_code == 401
    assert client.get(f"/{other}/api/dicts/mission", headers=h_there).json()["title"] == C.module(OTHER).UI["title"]
    start(client, h_here)
    # each dashboard lists only its own mission's students, and acts only on them
    t = teacher(client)
    mine_ = client.get("/api/teacher/dicts", headers=t).json()
    theirs = client.get(f"/{other}/api/teacher/dicts", headers=t).json()
    assert [s["id"] for s in mine_["students"]] == [here["student"]["id"]]
    assert [s["id"] for s in theirs["students"]] == [there["student"]["id"]]
    assert theirs["mission"] == OTHER and theirs["total_questions"] == C.module(OTHER).TOTAL
    assert client.post(f"/{other}/api/teacher/dicts/{here['student']['id']}/reset", headers=t).status_code == 404
    assert client.delete(f"/{other}/api/teacher/students/{here['student']['id']}", headers=t).status_code == 404
    assert client.get("/api/dicts/mission", headers=h_here).json()["state"]["started_at"]   # untouched


@needs_two
def test_each_mission_keeps_its_own_clock(client):
    other = C.slug(OTHER)
    h = {"Authorization": "Bearer " + client.post(f"/{other}/api/login", json=WHO).json()["token"]}
    st = client.post(f"/{other}/api/dicts/start", json={"accept_rules": True}, headers=h).json()["state"]
    want = float(os.environ.get("MISSION_MINUTES") or getattr(C.module(OTHER), "MISSION_MINUTES", 45)) * 60
    assert st["mission_seconds"] == want


def test_a_database_from_before_missions_is_upgraded(tmp_path):
    """Rows saved by a one-mission server belong to its mission; roll numbers then become unique per mission."""
    old = (
        "CREATE TABLE students(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, roll_no TEXT NOT NULL, "
        "roll_key TEXT NOT NULL UNIQUE, section TEXT NOT NULL, token TEXT UNIQUE, created_at REAL NOT NULL, last_seen REAL, "
        "state TEXT NOT NULL, university TEXT NOT NULL DEFAULT '', contact TEXT NOT NULL DEFAULT '')",
        "INSERT INTO students(name, roll_no, roll_key, section, created_at, state) VALUES('Old One', 'r1', 'R1', 'S-1', 1, '{}')",
    )
    if TEST_PG:
        db._run("DROP TABLE IF EXISTS students, events, teacher_tokens")
        db._run(old[0].replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY")
                .replace("REAL", "DOUBLE PRECISION"))
        db._run(old[1])
        db.connect(TEST_PG, "s30")
    else:
        import sqlite3
        path = str(tmp_path / "old.db")
        con = sqlite3.connect(path)
        for sql in old:
            con.execute(sql)
        con.commit()
        con.close()
        db.connect(path, "s30")
    rows = db.all_students("s30")
    assert [(r["name"], r["mission"]) for r in rows] == [("Old One", "s30")]
    assert db.by_roll("s30", "r1")["name"] == "Old One" and db.by_roll("s29", "r1") is None
    db.insert_student("s29", "New One", "r1", "S-1", "tok-new", {})        # same roll, other mission: allowed
    assert db.by_roll("s29", "r1")["name"] == "New One"
    with pytest.raises(Exception):
        db.insert_student("s30", "Clash", "R1", "S-1", "tok-clash", {})    # same roll, same mission: refused
    db.connect(TEST_PG or path, "s30")                                      # connecting again changes nothing
    assert len(db.all_students("s30")) == 1 and len(db.all_students("s29")) == 1
