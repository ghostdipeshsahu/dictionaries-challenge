"""Dictionaries mission engine: grading, XP, combo, stars, badges, timers and proctoring limits.

Pure functions over a per-student `state` dict, so the rules can be tested without HTTP.
Everything a learner could game (answers, XP, timers, unlocks) is decided here, never on the client.
"""
import math
import re
import time

from . import content as C

GRACE = 2.0  # seconds of network slack on a question deadline


class Rules:
    def __init__(self, mission_minutes=45, max_tab_switches=3, reveal_after=2):
        self.mission_seconds = int(mission_minutes * 60)
        self.max_tab_switches = int(max_tab_switches)
        self.reveal_after = int(reveal_after)

    def public(self):
        return {"mission_minutes": round(self.mission_seconds / 60), "max_tab_switches": self.max_tab_switches,
                "reveal_after": self.reveal_after}


class MissionError(Exception):
    """Maps to an HTTP error; `detail` is what the client shows (or matches, like 'mission-over')."""

    def __init__(self, detail, status=409):
        super().__init__(detail)
        self.detail, self.status = detail, status


# ---------------------------------------------------------------------------------------------
# output comparison: dictionaries keep insertion order, so lines must match exactly
def out_lines(s):
    lines = [ln.rstrip() for ln in str(s or "").replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def same_output(got, expected):
    g, e = out_lines(got), out_lines(expected)
    return len(g) == len(e) and all(a.strip() == b.strip() for a, b in zip(g, e))


def check_rules(q, code):
    """Static checks a coding challenge may add (e.g. 'use one dictionary'). Returns failed messages."""
    msgs = []
    for r in q.get("rules", []):
        if "require" in r and not re.search(r["require"], code or ""):
            msgs.append(r["msg"])
        if "forbid" in r and re.search(r["forbid"], code or ""):
            msgs.append(r["msg"])
    return msgs


# ---------------------------------------------------------------------------------------------
# public mission payload (no answer keys)
PUBLIC_FIELDS = ("id", "type", "title", "xp", "time", "concept", "level", "options", "code", "assertion", "reason",
                 "left", "right", "items", "categories", "errors", "goal", "start", "scenario", "boxes", "args")


def public_question(q):
    p = {k: q[k] for k in PUBLIC_FIELDS if k in q}
    if q["type"] == "coding":
        ch = q["challenge"]
        p["title"] = ch["title"]
        p["challenge"] = {
            "title": ch["title"], "statement": ch["statement"], "input_fmt": ch["input_fmt"],
            "output_fmt": ch["output_fmt"], "starter": ch["starter"], "compare": "exact",
            # Hidden tests send their input (the learner's browser runs the code) but never the expected output.
            "tests": [{"stdin": t["stdin"], "hidden": bool(t.get("hidden")),
                       **({} if t.get("hidden") else {"expected": t["expected"]})} for t in ch["tests"]],
        }
    return p


def mission_payload(rules):
    return {
        "title": C.UI["title"],
        "levels": [{"id": l["id"], "name": l["name"], "difficulty": l["difficulty"], "intel": l["intel"], "demo": l["demo"],
                    "learn": l.get("learn", []), "walk": l.get("walk", []),
                    **({"job": l["job"]} if l.get("job") else {}), **({"bonus": True} if l.get("bonus") else {}), **({"intel_title": l["intel_title"]} if l.get("intel_title") else {}),
                    "main": l["main"], "questions": [public_question(C.QUESTIONS[q]) for q in l["main"]]} for l in C.LEVELS],
        "badges": C.BADGES,
        "concepts": C.CONCEPTS,
        "type_labels": C.TYPE_LABEL,
        "ui": C.UI,
        "rules": rules.public(),
        "feedback": {"topic": C.FEEDBACK_TOPIC, "helped": [{"key": k, "emoji": e, "label": t} for k, e, t in C.FEEDBACK_HELPED]},
    }


# ---------------------------------------------------------------------------------------------
# state
def new_state():
    return normalize({"started_at": None, "ended_at": None, "ended_reason": None, "xp": 0, "combo": 0, "best_combo": 0,
                      "q": {}, "badges": [], "current": None, "answers": 0, "correct": 0,
                      "proctor": {"tab_switches": 0, "copy_paste": 0, "devtools": 0, "multi_tab": 0, "away_ms": 0}})


def normalize(state):
    """Fill fields added after the first release, so older saved states load (and can be resumed)."""
    state.setdefault("paused", 0.0)       # seconds the mission spent ended before a teacher resumed it (not counted as used)
    state.setdefault("grace", 0.0)        # extra seconds a teacher's resume added (a resume always leaves at least 5 minutes)
    state.setdefault("resumes", [])       # [{at, reason}] one entry per teacher resume
    state.setdefault("last_action", None)  # last real step by the learner (open, answer, hint, reveal, start)
    p = state["proctor"]
    p.setdefault("tab_total", p.get("tab_switches", 0))  # every switch ever; tab_switches counts since the last resume
    return state


def has_bonus():
    return any(l.get("bonus") for l in C.LEVELS)


def end_reason(state, reason):
    """Once every required stage is cleared the mission counts as complete, however it ends (bonus, Finish, clock, tabs)."""
    return "complete" if state.get("core_done_at") else reason


def deadline(state, rules):
    return state["started_at"] + rules.mission_seconds + state["paused"] + state["grace"]


def qst(state, qid):
    return state["q"].setdefault(qid, {"wrong": 0, "hints": 0, "solved": False, "revealed": False,
                                        "timed_out": False, "first": None, "deadline": None, "xp": 0})


def is_cleared(s):
    return bool(s and (s["solved"] or s["revealed"] or s["timed_out"]))


def tick(state, rules, now=None):
    """Apply the mission clock lazily. Returns True if this call ended the mission."""
    now = now or time.time()
    normalize(state)
    if state["started_at"] and not state["ended_at"] and now >= deadline(state, rules):
        state["ended_at"] = deadline(state, rules)
        state["ended_reason"] = end_reason(state, "time")
        return True
    return False


def live(state):
    return bool(state["started_at"] and not state["ended_at"])


def level_stats(state, lvl):
    total = len(lvl["main"])
    cleared = first = tout = 0
    for qid in lvl["main"]:
        s = state["q"].get(qid)
        if is_cleared(s):
            cleared += 1
        if s and s["solved"] and not s["wrong"]:
            first += 1
        if s and s["timed_out"]:
            tout += 1
    done = cleared == total
    stars = 0
    if done:
        stars = 3 if first == total else 2 if first >= math.ceil(total * 0.6) else 1
    return {"id": lvl["id"], "total": total, "cleared": cleared, "first_try": first, "timed_out": tout, "done": done, "stars": stars}


def unlocked_ids(state):
    out, prev_done = [], True
    for lvl in C.LEVELS:
        if prev_done:
            out.append(lvl["id"])
        prev_done = level_stats(state, lvl)["done"]
    return out


def concepts(state):
    agg = {}
    for qid, s in state["q"].items():
        if s["first"] is None or qid not in C.QUESTIONS:  # a question removed after this student answered it
            continue
        k = C.QUESTIONS[qid]["concept"]
        a = agg.setdefault(k, {"c": 0, "a": 0})
        a["a"] += 1
        a["c"] += 1 if s["first"] else 0
    return agg


def used_seconds(state, now=None):
    if not state["started_at"]:
        return 0
    end = state["ended_at"] or (now or time.time())
    return max(0, int(end - state["started_at"] - state.get("paused", 0)))


def public_state(state, rules, now=None):
    now = now or time.time()
    unl = unlocked_ids(state)
    levels = []
    for lvl in C.LEVELS:
        st = level_stats(state, lvl)
        st["unlocked"] = lvl["id"] in unl
        levels.append(st)
    done = sum(l["cleared"] for l, lv in zip(levels, C.LEVELS) if not lv.get("bonus"))
    return {
        "xp": state["xp"], "combo": state["combo"], "best_combo": state["best_combo"],
        "started_at": iso(state["started_at"]), "ended_at": iso(state["ended_at"]), "ended_reason": state["ended_reason"],
        # Exact seconds, not rounded down: the browser counts down from this, and must not reach 0:00
        # before the server's clock does (otherwise its "mission over" check finds the mission still running).
        "remaining": (round(max(0.0, deadline(state, rules) - now), 3) if live(state) else 0) if state["started_at"] else None,
        "mission_seconds": rules.mission_seconds + int(state.get("grace", 0)), "used_seconds": used_seconds(state, now),
        "progress": {"done": done, "total": C.TOTAL},
        "core_done": bool(state.get("core_done_at")),
        "feedback_done": bool(state.get("feedback")),
        "levels": levels,
        "questions": {qid: {"solved": s["solved"], "wrong": s["wrong"], "revealed": s["revealed"],
                            "timed_out": s["timed_out"], "hint": s["hints"] > 0} for qid, s in state["q"].items() if qid in C.QUESTIONS},
        "concepts": concepts(state),
        "badges": list(state["badges"]),
        "proctor": {"tab_switches": state["proctor"]["tab_switches"], "max_tab_switches": rules.max_tab_switches,
                    "copy_paste": state["proctor"]["copy_paste"]},
    }


def iso(ts):
    if not ts:
        return None
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


# ---------------------------------------------------------------------------------------------
# solutions + grading
def solution(q):
    t = q["type"]
    if t in ("mcq", "predict", "ar"):
        return {"index": q["answer"], "text": q["options"][q["answer"]]}
    if t == "msq":
        return {"indexes": q["answers"], "texts": [q["options"][i] for i in q["answers"]]}
    if t in ("tf", "numeric"):
        return {"value": q["value"]}
    if t == "fill":
        return {"blanks": [b[0] for b in q["blanks"]]}
    if t in ("match", "order", "categorize"):
        return {"mapping": q["mapping"]}
    if t == "debug":
        return {"line": q["line"], "error": q["error"], "error_text": q["errors"][q["error"]]}
    if t == "board":
        return {"rows": q["target"], "text": board_repr(q["target"])}
    if t == "land":
        return {"mapping": q["mapping"], "text": q["prints"]}
    if t == "coding":
        return {"solution": q["solution"]}
    return {}


def board_repr(rows):
    return "{" + ", ".join(f"{k!r}: {v!r}" for k, v in rows) + "}"


def _norm_blank(s):
    return re.sub(r"\s+", " ", str(s).strip())


def _int_list(ans, n):
    if not isinstance(ans, list) or len(ans) != n or not all(isinstance(x, int) and not isinstance(x, bool) for x in ans):
        raise MissionError("That answer is not in the right shape.", 422)
    return ans


def grade(q, ans, code=None):
    """Return (correct, detail). Raises MissionError(422) on a malformed answer."""
    t = q["type"]
    d = {}
    if t in ("mcq", "predict", "ar"):
        if not isinstance(ans, int) or isinstance(ans, bool) or not 0 <= ans < len(q["options"]):
            raise MissionError("Choose one of the options.", 422)
        ok = ans == q["answer"]
        if not ok and q.get("why", {}).get(ans):
            d["why_wrong"] = q["why"][ans]
        return ok, d
    if t == "msq":
        if not isinstance(ans, list) or not ans or not all(isinstance(x, int) and 0 <= x < len(q["options"]) for x in ans):
            raise MissionError("Choose at least one option.", 422)
        sel, key = set(ans), set(q["answers"])
        d.update(missing=len(key - sel), extra=len(sel - key))
        return sel == key, d
    if t == "tf":
        if not isinstance(ans, bool):
            raise MissionError("Choose True or False.", 422)
        return ans == q["value"], d
    if t == "numeric":
        try:
            v = float(ans)
        except (TypeError, ValueError):
            raise MissionError("Type a number.", 422)
        return math.isclose(v, float(q["value"])), d
    if t == "fill":
        if not isinstance(ans, list) or len(ans) != len(q["blanks"]):
            raise MissionError("Fill every gap.", 422)
        per = [_norm_blank(a) in [_norm_blank(x) for x in acc] for a, acc in zip(ans, q["blanks"])]
        d["per_blank"] = per
        return all(per), d
    if t in ("match", "categorize"):
        n = len(q["left"]) if t == "match" else len(q["items"])
        ans = _int_list(ans, n)
        per = [a == b for a, b in zip(ans, q["mapping"])]
        d.update(per_item=per, right_count=sum(per))
        return all(per), d
    if t == "order":
        ans = _int_list(ans, len(q["items"]))
        if sorted(ans) != list(range(len(q["items"]))):
            raise MissionError("Use every line exactly once.", 422)
        per = [a == b for a, b in zip(ans, q["mapping"])]
        d.update(right_count=sum(per))
        return all(per), d
    if t == "debug":
        if not isinstance(ans, dict) or not isinstance(ans.get("line"), int) or not isinstance(ans.get("error"), int):
            raise MissionError("Pick a line and what goes wrong.", 422)
        d.update(line_ok=ans["line"] == q["line"], error_ok=ans["error"] == q["error"])
        return d["line_ok"] and d["error_ok"], d
    if t == "board":
        rows = ans.get("rows") if isinstance(ans, dict) else None
        if not isinstance(rows, list) or len(rows) > 12:
            raise MissionError("Build the board first.", 422)
        clean = []
        for r in rows:
            if (not isinstance(r, list) or len(r) != 2 or not isinstance(r[0], str) or not 0 < len(r[0]) <= 16
                    or not isinstance(r[1], int) or isinstance(r[1], bool)):
                raise MissionError("Each row needs a name and a whole-number price.", 422)
            clean.append([r[0], r[1]])
        if len({r[0] for r in clean}) != len(clean):
            raise MissionError("A board cannot hold the same key twice.", 422)
        return board_check(q, clean, d)
    if t == "land":
        # one box per argument: an index into q["boxes"], or len(boxes) for "no box: Python stops"
        if not isinstance(ans, list) or len(ans) != len(q["args"]) or not all(
                isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= len(q["boxes"]) for x in ans):
            raise MissionError("Place every argument in a box.", 422)
        per = [a == b for a, b in zip(ans, q["mapping"])]
        d.update(per_item=per, right_count=sum(per))
        return all(per), d
    if t == "coding":
        tests = q["challenge"]["tests"]
        outs = ans.get("outputs") if isinstance(ans, dict) else None
        if not isinstance(outs, list) or len(outs) != len(tests):
            raise MissionError("Run every test before you submit.", 422)
        res = []
        for t_, o in zip(tests, outs):
            o = o if isinstance(o, dict) else {}
            err = o.get("error")
            et = (err.get("type") if isinstance(err, dict) else None) or None
            passed = not err and same_output(str(o.get("stdout", ""))[:20000], t_["expected"])
            item = {"passed": passed, "hidden": bool(t_.get("hidden"))}
            if t_.get("hidden") and not passed and t_.get("note"):
                item["note"] = t_["note"]
            if et:
                item["error"] = et
            res.append(item)
        d["tests"] = res
        ok = all(r["passed"] for r in res)
        if ok:
            broken = check_rules(q, code)
            if broken:
                d["why_wrong"] = "Every test passes, but: " + " ".join(broken)
                return False, d
        return ok, d
    raise MissionError("Unknown question type.", 500)


def board_check(q, rows, d):
    target = q["target"]
    want = dict((k, v) for k, v in target)
    got = dict((k, v) for k, v in rows)
    checks = [{"ok": rows == target, "text": f"print(menu) gives <code>{_html(board_repr(rows))}</code>"}]
    for k, v in target:
        if k not in got:
            checks.append({"ok": False, "text": f"<code>{_html(repr(k))}</code> should be on the board"})
        elif got[k] != v:
            checks.append({"ok": False, "text": f"<code>{_html(repr(k))}</code> has the wrong price"})
    for k in got:
        if k not in want:
            checks.append({"ok": False, "text": f"<code>{_html(repr(k))}</code> should not be on the board"})
    if rows != target and [r[0] for r in rows] != [r[0] for r in target] and set(got) == set(want) and got == want:
        checks.append({"ok": False, "text": "Every row and price is right, but the order is not. A changed key keeps its place; a new key goes to the end."})
    d["checks"] = checks
    return rows == target, d


def _html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def xp_for(q, s, combo):
    base = q["xp"]
    if s["wrong"] == 0:
        award = base
        clean = round(base * 0.2) if s["hints"] == 0 else 0
    else:
        award, clean = round(base * 0.6), 0
    hint_cost = s["hints"] * max(1, round(base * 0.1))
    award = max(round(base * 0.3), award - hint_cost)
    combo_bonus = min(combo - 2, 5) * 2 if combo >= 3 else 0
    return award + clean + combo_bonus, {"base": award, "clean": clean, "combo": combo_bonus, "hint_cost": hint_cost if s["hints"] else 0}


# ---------------------------------------------------------------------------------------------
# badges + stage completion
def award_badges(state, now=None):
    new = []

    def give(b):
        if b not in state["badges"]:
            state["badges"].append(b)
            new.append(b)

    stars3 = False
    for lvl in C.LEVELS:
        st = level_stats(state, lvl)
        if st["done"]:
            if lvl["id"] in C.STAGE_BADGE:
                give(C.STAGE_BADGE[lvl["id"]])
            if st["stars"] == 3:
                stars3 = True
    if stars3:
        give("clean-sweep")
    if state["best_combo"] >= 5:
        give("combo-5")
    vtype, vbadge = C.VISUAL_PRO
    visual = [qid for qid, q in C.QUESTIONS.items() if q["type"] == vtype]
    if visual and all(state["q"].get(b, {}).get("solved") and not state["q"][b]["wrong"] for b in visual):
        give(vbadge)
    if level_stats(state, C.LEVEL_BY_ID["BOSS"])["done"] and not state["ended_at"]:
        if has_bonus() and not all(level_stats(state, l)["done"] for l in C.LEVELS if l.get("bonus")):
            # Every required stage is cleared: the mission is complete, and the bonus round stays open until the
            # student finishes it, presses Finish, or the clock runs out.
            state.setdefault("core_done_at", now or time.time())
        else:
            state.setdefault("core_done_at", now or time.time())
            state["ended_at"] = now or time.time()
            state["ended_reason"] = "complete"
    return new


# ---------------------------------------------------------------------------------------------
# actions (each takes the state, mutates it, returns the response body)
def _question(state, qid, need_live=True):
    q = C.QUESTIONS.get(qid)
    if not q:
        raise MissionError("Unknown question.", 404)
    if need_live:
        if not state["started_at"]:
            raise MissionError("Start the mission first.", 409)
        if state["ended_at"]:
            raise MissionError("mission-over", 409)
    if q["stage"] not in unlocked_ids(state):
        raise MissionError("Clear the stage before this one first.", 403)
    return q


def start(state, rules, accept, now=None):
    if not accept:
        raise MissionError("Accept the rules to start.", 422)
    if not state["started_at"]:
        state["started_at"] = now or time.time()
    state["last_action"] = now or time.time()
    return {"state": public_state(state, rules, now)}


def open_q(state, rules, qid, now=None):
    now = now or time.time()
    q = _question(state, qid)
    s = qst(state, qid)
    state["current"] = qid
    state["last_action"] = now
    if is_cleared(s):
        return {"cleared": True}
    if not s["deadline"]:
        s["deadline"] = now + q["time"]
    return {"cleared": False, "remaining": max(0, s["deadline"] - now), "limit": q["time"]}


def _close_timeout(state, q, s):
    s["timed_out"] = True
    if s["first"] is None:
        s["first"] = False
    state["combo"] = 0


def _closing_body(state, rules, q, now):
    new = award_badges(state, now)
    return {"state": public_state(state, rules, now), "solution": solution(q), "explain": q["explain"],
            "trap": q.get("trap"), "focus": q.get("focus"), "new_badges": new}


def expire(state, rules, qid, now=None):
    now = now or time.time()
    q = _question(state, qid)
    s = qst(state, qid)
    if not is_cleared(s):
        if not s["deadline"] or now < s["deadline"] - 1.5:
            raise MissionError("This question still has time left.", 409)
        _close_timeout(state, q, s)
    return _closing_body(state, rules, q, now)


def hint(state, rules, qid):
    q = _question(state, qid)
    s = qst(state, qid)
    state["last_action"] = time.time()
    if not is_cleared(s) and s["hints"] < len(q["hints"]):
        s["hints"] += 1
    n = max(1, s["hints"])
    return {"concept": q["concept"], "hints": q["hints"][:n], "more": n < len(q["hints"]) and not is_cleared(s)}


def reveal(state, rules, qid, now=None):
    now = now or time.time()
    q = _question(state, qid)
    s = qst(state, qid)
    state["last_action"] = now
    if not is_cleared(s):
        if s["wrong"] < rules.reveal_after:
            raise MissionError(f"The solution opens after {rules.reveal_after} wrong tries.", 403)
        s["revealed"] = True
        state["combo"] = 0
    return _closing_body(state, rules, q, now)


def answer(state, rules, qid, ans, code=None, now=None):
    now = now or time.time()
    q = _question(state, qid)
    s = qst(state, qid)
    state["last_action"] = now
    if is_cleared(s):
        # replay or a second look: graded for practice, nothing changes
        ok, d = grade(q, ans, code)
        body = {"correct": ok, "already_solved": True, "xp": 0, "detail": d, "combo": state["combo"],
                "wrong_count": s["wrong"], "can_reveal": False, "hint_used": s["hints"] > 0, "new_badges": [],
                "state": public_state(state, rules, now)}
        if ok:
            body.update(explain=q["explain"], trap=q.get("trap"), focus=q.get("focus"))
        return body
    if not s["deadline"]:
        s["deadline"] = now + q["time"]
    if now > s["deadline"] + GRACE:
        _close_timeout(state, q, s)
        body = _closing_body(state, rules, q, now)
        body["timed_out"] = True
        return body
    ok, d = grade(q, ans, code)
    state["answers"] += 1
    if s["first"] is None:
        s["first"] = ok
    xp, parts = 0, {}
    if ok:
        state["correct"] += 1
        s["solved"] = True
        state["combo"] += 1
        state["best_combo"] = max(state["best_combo"], state["combo"])
        xp, parts = xp_for(q, s, state["combo"])
        s["xp"] = xp
        state["xp"] += xp
    else:
        s["wrong"] += 1
        state["combo"] = 0
    new = award_badges(state, now)
    body = {"correct": ok, "xp": xp, "xp_parts": parts, "detail": d, "combo": state["combo"], "wrong_count": s["wrong"],
            "can_reveal": (not ok) and s["wrong"] >= rules.reveal_after, "hint_used": s["hints"] > 0,
            "new_badges": new, "state": public_state(state, rules, now)}
    if ok:
        body.update(explain=q["explain"], trap=q.get("trap"), focus=q.get("focus"))
    return body


PROCTOR_TYPES = {"tab_switch", "copy", "cut", "paste", "contextmenu", "devtools", "multi_tab"}


def proctor(state, rules, kind, duration_ms=0, now=None):
    now = now or time.time()
    if kind not in PROCTOR_TYPES:
        raise MissionError("Unknown event.", 422)
    p = state["proctor"]
    counted = ended = False
    if live(state):
        if kind == "tab_switch":
            p["tab_switches"] += 1
            p["tab_total"] = p.get("tab_total", 0) + 1
            p["away_ms"] += max(0, int(duration_ms or 0))
            counted = True
            if rules.max_tab_switches and p["tab_switches"] >= rules.max_tab_switches:
                state["ended_at"] = now
                state["ended_reason"] = end_reason(state, "proctor")
                ended = True
        elif kind in ("copy", "cut", "paste", "contextmenu"):
            p["copy_paste"] += 1
        elif kind == "devtools":
            p["devtools"] += 1
    if kind == "multi_tab":
        p["multi_tab"] += 1
    return {"state": public_state(state, rules, now), "counted": counted, "ended": ended,
            "tab_switches": p["tab_switches"], "max": rules.max_tab_switches}


def review(state):
    items = []
    for lvl in C.LEVELS:
        for qid in lvl["main"]:
            s = state["q"].get(qid)
            if not s or not (s["wrong"] or s["revealed"] or s["timed_out"]):
                continue
            q = C.QUESTIONS[qid]
            items.append({"qid": qid, "level": lvl["id"], "title": q["challenge"]["title"] if q["type"] == "coding" else q["title"],
                          "explain": q["explain"], "trap": q.get("trap"), "wrong": s["wrong"], "revealed": s["revealed"],
                          "timed_out": s["timed_out"]})
    return {"items": items}


STATUS_LABEL = {"complete": "Completed", "time": "Time ran out", "proctor": "Ended: tab switches",
                "in progress": "In progress", "not started": "Not started"}


def finish(state, rules, now=None):
    """A student who cleared every required stage ends the mission now instead of playing the bonus round."""
    now = now or time.time()
    if not state.get("core_done_at"):
        raise MissionError("Clear the Final Boss first.", 409)
    if not state["ended_at"]:
        state["ended_at"] = now
        state["ended_reason"] = "complete"
    return {"state": public_state(state, rules, now)}


def status_of(state):
    if state["ended_reason"]:
        return state["ended_reason"]
    if state.get("core_done_at"):
        return "complete"
    return "in progress" if state["started_at"] else "not started"


# ---------------------------------------------------------------------------------------------
# end-of-mission feedback
FEEDBACK_DIFFICULTY = {"easy": "Too easy", "right": "Just right", "hard": "Too hard"}
FEEDBACK_PACE = {"spare": "Time to spare", "enough": "Just enough", "more": "Needed more time"}
FEEDBACK_TECH = {"no": "No", "small": "Yes, small ones", "blocked": "Yes, it blocked me"}


def _scale(v, name):
    if not isinstance(v, int) or isinstance(v, bool) or not 1 <= v <= 5:
        raise MissionError(f"Pick {name} on the 1 to 5 scale.", 422)
    return v


def feedback(state, rules, fb, now=None):
    """Save the learner's feedback. Asked once, when the mission has ended; a repeat send is ignored.
    Name, roll number, section, university and contact come from the sign-in, so they are not asked here."""
    now = now or time.time()
    if not state["ended_at"]:
        raise MissionError("Feedback opens when your mission ends.", 409)
    if state.get("feedback"):
        return {"state": public_state(state, rules, now), "already": True}
    stages = [l["id"] for l in C.LEVELS if not l.get("bonus")]
    if fb.get("toughest") not in stages or fb.get("favourite") not in stages:
        raise MissionError("Splat the toughest stage and star your favourite.", 422)
    for key, labels, what in (("difficulty", FEEDBACK_DIFFICULTY, "how difficult it was"),
                              ("pace", FEEDBACK_PACE, "how the time was"), ("tech", FEEDBACK_TECH, "about technical problems")):
        if fb.get(key) not in labels:
            raise MissionError(f"Tell us {what}.", 422)
    keys = [k for k, _, _ in C.FEEDBACK_HELPED]
    helped = [k for k in keys if k in (fb.get("helped") or [])]
    if not helped:
        raise MissionError("Pick at least one thing that helped you learn.", 422)
    done = sum(level_stats(state, l)["cleared"] for l in C.LEVELS if not l.get("bonus"))
    state["feedback"] = {
        "enjoy": _scale(fb.get("enjoy"), "how much you enjoyed it"),
        "confidence": _scale(fb.get("confidence"), "your confidence"),
        "toughest": fb["toughest"], "favourite": fb["favourite"],
        "difficulty": fb["difficulty"], "pace": fb["pace"], "helped": helped, "tech": fb["tech"],
        "improve": str(fb.get("improve") or "").strip()[:600],
        # how far the learner got, recorded by the app (not asked)
        "reached": {"done": done, "total": C.TOTAL, "status": status_of(state),
                    "bonus": any(level_stats(state, l)["done"] for l in C.LEVELS if l.get("bonus"))},
        "at": now,
    }
    return {"state": public_state(state, rules, now)}


RESUME_MIN_SECONDS = 300


def resume(state, rules, now=None):
    """Teacher action: reopen a mission that ended on tab switches or time, from where the learner stopped.

    Nothing the learner earned is touched. The time the mission spent ended is not counted, so the learner gets
    back exactly the time they had left (at least 5 minutes), the open question keeps its remaining seconds,
    and the tab-switch limit starts again (the total stays visible to the teacher)."""
    now = now or time.time()
    normalize(state)
    if not state["started_at"] or not state["ended_at"] or state["ended_reason"] not in ("proctor", "time"):
        raise MissionError("Only a mission that ended on tab switches or time can be resumed.", 409)
    pause = max(0.0, now - state["ended_at"])
    state["paused"] += pause
    for s in state["q"].values():
        if s.get("deadline") and not is_cleared(s):
            s["deadline"] += pause
    state["resumes"].append({"at": now, "reason": state["ended_reason"]})
    state["ended_at"] = state["ended_reason"] = None
    left = deadline(state, rules) - now
    if left < RESUME_MIN_SECONDS:
        state["grace"] += RESUME_MIN_SECONDS - left
    state["proctor"]["tab_switches"] = 0
    state["last_action"] = now
    return {"state": public_state(state, rules, now)}


def current_of(state):
    """Where the learner is (or stopped): the last question they opened. None before the start and after completion."""
    qid = state.get("current")
    if not qid or qid not in C.QUESTIONS or not state["started_at"] or state["ended_reason"] == "complete":
        return None
    q = C.QUESTIONS[qid]
    lvl = C.LEVEL_BY_ID[q["stage"]]
    s = state["q"].get(qid)
    return {"stage": lvl["name"], "qid": qid, "n": lvl["main"].index(qid) + 1, "of": len(lvl["main"]),
            "title": q["challenge"]["title"] if q["type"] == "coding" else q["title"], "cleared": is_cleared(s)}
