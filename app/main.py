"""Dictionaries: The Python Challenge · FastAPI backend.

Same endpoint design as the Set Operations app, under /api/dicts and /api/teacher/dicts.
Run:  uvicorn app.main:app --port 8000
"""
import asyncio
import csv
import hmac
import io
import json
import os
import re
import secrets
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import content as C
from . import db
from . import engine as E

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

CLASS_CODE = os.environ.get("CLASS_CODE", "").strip()
# Set TEACHER_PASSWORD in the environment. The fallback is for a laptop demo only.
TEACHER_PASSWORD = os.environ.get("TEACHER_PASSWORD") or "change-me"
RULES = E.Rules(mission_minutes=float(os.environ.get("MISSION_MINUTES") or getattr(C, "MISSION_MINUTES", 45)),
                max_tab_switches=int(os.environ.get("MAX_TAB_SWITCHES", "3")),
                reveal_after=int(os.environ.get("REVEAL_AFTER", "2")))
ONLINE_WINDOW = 75        # seconds since the last heartbeat that still counts as "signed in right now"
IDLE_SECONDS = int(os.environ.get("IDLE_SECONDS", "120"))  # page open, mission running, but no step for this long
DEVICE_LOCK = 75          # a roll number signed in elsewhere within this window cannot sign in again
TEACHER_TOKEN_AGE = 12 * 3600

def _build_id():
    """Fingerprint of the front-end files. An open dashboard compares it and reloads itself after an update."""
    import hashlib
    h = hashlib.sha1()
    for f in sorted(STATIC.rglob("*")):
        if f.is_file() and f.suffix in (".html", ".js", ".css") and "vendor" not in f.parts:
            h.update(f.name.encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:12]


BUILD = _build_id()


class NoCacheStatic(StaticFiles):
    """Browsers must re-check scripts and styles on every load (cheap: unchanged files answer 304 via ETag),
    so a reload never runs an old copy. The large Pyodide runtime may be cached."""

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        if not path.startswith("vendor/"):
            resp.headers["Cache-Control"] = "no-cache"
        return resp


app = FastAPI(title=C.UI["title"], version="1.1.0")
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or ""
if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    STORAGE = "postgres"
    db.connect(DATABASE_URL)
elif os.environ.get("VERCEL"):
    # Vercel's disk is temporary: anything written here disappears. Run, but warn loudly on the dashboard.
    STORAGE = "temporary"
    db.connect(os.environ.get("DB_PATH", "/tmp/dicts.db"))
else:
    STORAGE = "sqlite"
    db.connect(os.environ.get("DB_PATH", str(ROOT / "data" / "dicts.db")))
# On Vercel each request may land on a different short-lived server, so a long-lived push stream cannot see
# every change. The dashboard then polls every 5 seconds instead (it does this by itself when push is False).
LIVE_PUSH = not os.environ.get("VERCEL")


@app.exception_handler(E.MissionError)
async def _mission_error(_req, exc: E.MissionError):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status)


# ---------- request bodies (same shapes as the Sets app) ----------
class LoginIn(BaseModel):
    name: str
    roll_no: str
    section: str
    university: str = ""
    contact: str = ""
    class_code: Optional[str] = None


class StartIn(BaseModel):
    accept_rules: bool = False


class QidIn(BaseModel):
    qid: str


class AnswerIn(BaseModel):
    qid: str
    answer: Any = None
    code: Optional[str] = Field(default=None, max_length=8000)


class ProctorIn(BaseModel):
    type: str
    duration_ms: int = 0
    qid: Optional[str] = None


class FeedbackIn(BaseModel):
    enjoy: Optional[int] = None
    toughest: str = Field(default="", max_length=12)
    favourite: str = Field(default="", max_length=12)
    difficulty: str = Field(default="", max_length=20)
    pace: str = Field(default="", max_length=20)
    confidence: Optional[int] = None
    helped: list[str] = Field(default_factory=list, max_length=20)
    tech: str = Field(default="", max_length=20)
    improve: str = Field(default="", max_length=2000)


class TeacherLoginIn(BaseModel):
    password: str


# ---------- auth ----------
def bearer(authorization: Optional[str]):
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def student(authorization: Optional[str] = Header(default=None)):
    with db.tx():
        s = db.by_token(bearer(authorization))
    if not s:
        raise HTTPException(401, "Sign in to continue.")
    return s


def teacher(authorization: Optional[str] = Header(default=None)):
    with db.tx():
        ok = db.teacher_token_ok(bearer(authorization), TEACHER_TOKEN_AGE)
    if not ok:
        raise HTTPException(401, "Teacher sign-in needed.")
    return True


def public_student(s):
    return {"id": s["id"], "name": s["name"], "roll_no": s["roll_no"], "section": s["section"],
            "university": s.get("university") or ""}


def clean(text, n):
    return " ".join(str(text or "").split())[:n]


# ---------- shared ----------
@app.get("/api/health")
def health():
    return {"ok": True, "app": "dictionaries", "class_code_required": bool(CLASS_CODE), "build": BUILD,
            "storage": STORAGE, "mission": C.MISSION, "title": C.UI["title"], "short": C.UI["short"]}


@app.post("/api/login")
def login(body: LoginIn):
    name, roll, section = clean(body.name, 60), clean(body.roll_no, 30), clean(body.section, 40).upper()
    university = clean(body.university, 120)
    phone = re.fullmatch(r"(?:\+?91|0)?([6-9]\d{9})", re.sub(r"[\s-]", "", body.contact or ""))
    if not name or not roll or not section or not university or not (body.contact or "").strip():
        raise HTTPException(422, "Fill in every field to join.")
    if not db.section_key(section):
        raise HTTPException(422, "Type your section, for example S-001.")
    if len(university) < 2:
        raise HTTPException(422, "Type your university name.")
    if not phone:
        raise HTTPException(422, "Type a 10-digit mobile number.")
    if CLASS_CODE and not hmac.compare_digest((body.class_code or "").strip().upper(), CLASS_CODE.upper()):
        raise HTTPException(403, "That class code is not right. Ask your teacher.")
    token = secrets.token_urlsafe(24)
    try:
        return _login(name, roll, section, token, university, phone.group(1))
    except HTTPException:
        raise
    except Exception as e:  # the same roll number signing in twice at the same instant (unique key)
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(409, "That sign-in clashed with another one for this roll number. Try again.")
        raise


def _login(name, roll, section, token, university, contact):
    with db.tx():
        s = db.by_roll(roll)
        if s:
            if s["name"].casefold() != name.casefold() or db.section_key(s["section"]) != db.section_key(section):
                raise HTTPException(409, "This roll number is already used by another student. Check it, or ask your teacher.")
            if s["token"] and s["last_seen"] and time.time() - s["last_seen"] < DEVICE_LOCK:
                raise HTTPException(409, "This roll number is signed in on another device. Sign out there, or ask your teacher to release it.")
            db.set_token(s["id"], token)
            if not s.get("university") or not s.get("contact"):  # signed up before these fields
                db.fill_profile(s["id"], university, contact)
            s = db.by_id(s["id"])
        else:
            sid = db.insert_student(name, roll, db.known_section(section) or section, token, E.new_state(), university, contact)
            s = db.by_id(sid)
    return {"token": token, "student": public_student(s)}


@app.post("/api/logout")
def logout(s=Depends(student)):
    with db.tx():
        db.set_token(s["id"], None, seen=False)
    return {"ok": True}


@app.get("/api/me")
def me(s=Depends(student)):
    with db.tx():
        db.touch(s["id"])
    return {"student": public_student(s)}


@app.post("/api/ping")
def ping(s=Depends(student)):
    with db.tx():
        cur = db.by_id(s["id"], lock=True)
        if E.tick(cur["state"], RULES):
            db.save_state(cur["id"], cur["state"])
        else:
            db.touch(s["id"])
    return {"ok": True}


# ---------- mission ----------
def mutate(s, fn, *args, **kw):
    """Load fresh state under the lock, apply the clock, run an engine action, save."""
    with db.tx():
        cur = db.by_id(s["id"], lock=True)
        st = cur["state"]
        E.tick(st, RULES)
        try:
            body = fn(st, RULES, *args, **kw)
        finally:
            db.save_state(cur["id"], st)
    return body


@app.get("/api/dicts/mission")
def mission(s=Depends(student)):
    with db.tx():
        cur = db.by_id(s["id"], lock=True)
        if E.tick(cur["state"], RULES):
            db.save_state(cur["id"], cur["state"])
    m = E.mission_payload(RULES)
    m["state"] = E.public_state(cur["state"], RULES)
    return m


@app.post("/api/dicts/start")
def start(body: StartIn, s=Depends(student)):
    return mutate(s, E.start, body.accept_rules)


@app.post("/api/dicts/open")
def open_question(body: QidIn, s=Depends(student)):
    return mutate(s, E.open_q, body.qid)


@app.post("/api/dicts/expire")
def expire(body: QidIn, s=Depends(student)):
    return mutate(s, E.expire, body.qid)


@app.post("/api/dicts/hint")
def hint(body: QidIn, s=Depends(student)):
    return mutate(s, E.hint, body.qid)


@app.post("/api/dicts/reveal")
def reveal(body: QidIn, s=Depends(student)):
    return mutate(s, E.reveal, body.qid)


@app.post("/api/dicts/answer")
def answer(body: AnswerIn, s=Depends(student)):
    return mutate(s, E.answer, body.qid, body.answer, body.code)


@app.post("/api/dicts/finish")
def finish(s=Depends(student)):
    return mutate(s, E.finish)


@app.post("/api/dicts/feedback")
def feedback(body: FeedbackIn, s=Depends(student)):
    return mutate(s, E.feedback, body.model_dump())


@app.post("/api/dicts/proctor")
def proctor(body: ProctorIn, s=Depends(student)):
    with db.tx():
        db.log_event(s["id"], body.type[:20], (body.qid or "")[:12] or None, max(0, min(body.duration_ms, 86_400_000)))
    return mutate(s, E.proctor, body.type, body.duration_ms)


@app.get("/api/dicts/review")
def review(s=Depends(student)):
    with db.tx():
        cur = db.by_id(s["id"], lock=True)
    return E.review(cur["state"])


def rank_key(st, now):
    ps = E.public_state(st["state"], RULES, now)
    return (-ps["xp"], -ps["progress"]["done"], ps["used_seconds"] or 10**9)


@app.get("/api/dicts/leaderboard")
def leaderboard(s=Depends(student)):
    now = time.time()
    with db.tx():
        mates = [x for x in db.all_students(s["section"]) if x["state"]["started_at"] or x["id"] == s["id"]]
    for x in mates:
        E.tick(x["state"], RULES, now)
    mates.sort(key=lambda x: rank_key(x, now))
    rows, me_row = [], None
    for i, x in enumerate(mates, 1):
        ps = E.public_state(x["state"], RULES, now)
        r = {"rank": i, "name": x["name"], "xp": ps["xp"], "done": ps["progress"]["done"], "total": C.TOTAL,
             "status": E.STATUS_LABEL[E.status_of(x["state"])].lower(), "me": x["id"] == s["id"]}
        if r["me"]:
            me_row = {"rank": i, "xp": ps["xp"]}
        if i <= 10:
            rows.append(r)
    return {"section": s["section"], "rows": rows, "me": me_row, "count": len(mates)}


# ---------- teacher ----------
@app.post("/api/teacher/login")
def teacher_login(body: TeacherLoginIn):
    if not hmac.compare_digest(body.password.encode(), TEACHER_PASSWORD.encode()):
        raise HTTPException(401, "That password is not right.")
    token = secrets.token_urlsafe(24)
    with db.tx():
        db.add_teacher_token(token)
    return {"token": token}


def dashboard(section=None):
    now = time.time()
    with db.tx():
        studs = db.all_students(section or None)
        all_sections = db.sections()
    rows = []
    stage_cleared = {l["id"]: 0 for l in C.LEVELS}
    concept_tot, type_tot = {}, {}
    answers = correct = 0
    for x in studs:
        st = x["state"]
        E.tick(st, RULES, now)
        ps = E.public_state(st, RULES, now)
        answers += st["answers"]
        correct += st["correct"]
        for l in ps["levels"]:
            if l["done"]:
                stage_cleared[l["id"]] += 1
        for qid, q in st["q"].items():
            if q["first"] is None or qid not in C.QUESTIONS:  # removed after it was answered
                continue
            qq = C.QUESTIONS[qid]
            for bucket, k in ((concept_tot, qq["concept"]), (type_tot, qq["type"])):
                b = bucket.setdefault(k, [0, 0])
                b[0] += 1 if q["first"] else 0
                b[1] += 1
        status = E.status_of(st)
        qv = st["q"].values()
        online = bool(x["token"] and x["last_seen"] and now - x["last_seen"] < ONLINE_WINDOW)
        # activity while the mission runs: active, idle (page open, no step for IDLE_SECONDS) or offline (page gone)
        activity, idle_for = None, 0
        if E.live(st):
            idle_for = int(now - (st.get("last_action") or st["started_at"]))
            activity = "offline" if not online else "idle" if idle_for >= IDLE_SECONDS else "active"
        rows.append({
            "id": x["id"], "name": x["name"], "roll_no": x["roll_no"], "section": x["section"],
            "university": x.get("university") or "", "contact": x.get("contact") or "", "status": status, "status_label": E.STATUS_LABEL[status], "xp": ps["xp"],
            "done": ps["progress"]["done"], "total": C.TOTAL,
            "first_try": sum(1 for q in qv if q["solved"] and not q["wrong"]),
            "timed_out": sum(1 for q in qv if q["timed_out"]),
            "revealed": sum(1 for q in qv if q["revealed"]),
            "used_minutes": round(ps["used_seconds"] / 60),
            "tab_switches": st["proctor"].get("tab_total", st["proctor"]["tab_switches"]),
            "tab_switches_now": st["proctor"]["tab_switches"], "copy_paste": st["proctor"]["copy_paste"],
            "activity": activity, "idle_seconds": idle_for, "resumes": len(st.get("resumes", [])),
            "can_resume": st["ended_reason"] in ("proctor", "time"), "feedback_sent": bool(st.get("feedback")),
            "multi_tab": st["proctor"]["multi_tab"], "devtools": st["proctor"]["devtools"],
            "concepts": {k: v["c"] / v["a"] for k, v in ps["concepts"].items()},
            "last_seen": E.iso(x["last_seen"]), "online": online, "current": E.current_of(st),
            "stars": sum(l["stars"] for l in ps["levels"]),
        })
    rows.sort(key=lambda r: (-r["xp"], -r["done"], r["used_minutes"] if r["status"] != "not started" else 10**9, r["name"].lower()))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    started = [r for r in rows if r["status"] != "not started"]
    overview = {
        "students": len(rows), "started": len(started), "online": sum(r["online"] for r in rows),
        "completed": sum(r["status"] == "complete" for r in rows),
        "avg_done": round(sum(r["done"] for r in started) / len(started), 1) if started else 0,
        "accuracy": (correct / answers) if answers else None, "answers": answers,
        "flagged": sum(1 for r in rows if r["tab_switches"] or r["copy_paste"] or r["multi_tab"] or r["devtools"]),
        "attention": sum(1 for r in rows if r["activity"] in ("idle", "offline") or r["can_resume"]),
    }
    feedback = feedback_summary(studs, rows)
    acc = lambda t: sorted(({"key": k, "accuracy": c / n, "answers": n} for k, (c, n) in t.items()), key=lambda d: d["accuracy"])
    return {
        "section": section or "", "sections": all_sections, "total_questions": C.TOTAL, "max_tab_switches": RULES.max_tab_switches,
        "mission_minutes": round(RULES.mission_seconds / 60), "mission": C.MISSION, "title": C.UI["title"], "short": C.UI["short"],
        "concept_labels": C.CONCEPTS, "type_labels": C.TYPE_LABEL, "idle_minutes": round(IDLE_SECONDS / 60, 1),
        "overview": overview,
        "stages": [{"id": l["id"], "name": l["name"], "cleared": stage_cleared[l["id"]], "total": len(l["main"])} for l in C.LEVELS],
        "concepts": [{"concept": d["key"], "accuracy": d["accuracy"], "answers": d["answers"]} for d in acc(concept_tot)],
        "types": [{"qtype": d["key"], "accuracy": d["accuracy"], "answers": d["answers"]} for d in acc(type_tot)],
        "feedback": feedback,
        "students": rows, "version": db.VERSION["n"], "server_time": E.iso(now), "build": BUILD, "push": LIVE_PUSH, "storage": STORAGE,
    }


HELPED_LABEL = {k: f"{e} {t}" for k, e, t in C.FEEDBACK_HELPED}


def feedback_summary(studs, rows):
    """The class's end-of-mission feedback: averages, counts, and every response (newest first).
    Who sent it (name, roll, section, university, contact) comes from the sign-in."""
    stage_name = {l["id"]: l["name"] for l in C.LEVELS}
    resp = []
    for x in studs:
        f = x["state"].get("feedback")
        if not f or "pace" not in f:  # skip drafts of an older feedback form
            continue
        reached = f["reached"]
        resp.append({
            "id": x["id"], "name": x["name"], "roll_no": x["roll_no"], "section": x["section"],
            "university": x.get("university") or "", "contact": x.get("contact") or "",
            "enjoy": f["enjoy"], "confidence": f["confidence"],
            "toughest": f["toughest"], "toughest_label": stage_name.get(f["toughest"], f["toughest"]),
            "favourite": f["favourite"], "favourite_label": stage_name.get(f["favourite"], f["favourite"]),
            "difficulty": f["difficulty"], "difficulty_label": E.FEEDBACK_DIFFICULTY[f["difficulty"]],
            "pace": f["pace"], "pace_label": E.FEEDBACK_PACE[f["pace"]],
            "tech": f["tech"], "tech_label": E.FEEDBACK_TECH[f["tech"]],
            "helped": [HELPED_LABEL.get(k, k) for k in f["helped"]], "improve": f["improve"],
            "reached": f"{reached['done']}/{reached['total']}" + (" + bonus" if reached.get("bonus") else ""),
            "status_label": E.STATUS_LABEL.get(reached["status"], reached["status"]), "at": E.iso(f["at"]),
        })
    resp.sort(key=lambda r: r["at"] or "", reverse=True)
    n = len(resp)
    avg = lambda k: round(sum(r[k] for r in resp) / n, 1) if n else None
    count = lambda k, labels: [{"key": key, "label": lab, "count": sum(r[k] == key for r in resp)} for key, lab in labels.items()]
    helped = {}
    for x in studs:
        for k in (x["state"].get("feedback") or {}).get("helped", []):
            helped[k] = helped.get(k, 0) + 1
    core = {l["id"]: l["name"] for l in C.LEVELS if not l.get("bonus")}
    ended = sum(1 for r in rows if r["status"] in ("complete", "time", "proctor"))
    return {
        "count": n, "ended": ended, "pending": ended - n if ended > n else 0,
        "enjoy": avg("enjoy"), "confidence": avg("confidence"),
        "needed_more_time": sum(r["pace"] == "more" for r in resp),
        "enjoy_dist": [sum(r["enjoy"] == i for r in resp) for i in range(1, 6)],
        "confidence_dist": [sum(r["confidence"] == i for r in resp) for i in range(1, 6)],
        "toughest": count("toughest", core), "favourite": count("favourite", core),
        "difficulty": count("difficulty", E.FEEDBACK_DIFFICULTY), "pace": count("pace", E.FEEDBACK_PACE),
        "tech": count("tech", E.FEEDBACK_TECH),
        "helped": sorted(({"key": k, "label": HELPED_LABEL[k], "count": helped.get(k, 0)} for k in HELPED_LABEL),
                         key=lambda d: -d["count"]),
        "responses": resp,
    }


@app.get("/api/teacher/dicts")
def teacher_dicts(section: str = "", _t=Depends(teacher)):
    return dashboard(section)


@app.get("/api/teacher/dicts/stream")
async def teacher_stream(request: Request, token: str = Query(...), section: str = ""):
    """Server-sent events: pushes the dashboard whenever anything changes (checked every second)."""
    with db.tx():
        if not db.teacher_token_ok(token, TEACHER_TOKEN_AGE):
            raise HTTPException(401, "Teacher sign-in needed.")
    if not LIVE_PUSH:
        raise HTTPException(404, "Live push is off on this host; the dashboard polls every 5 seconds.")

    async def gen():
        last, last_sent = -1, 0.0
        yield "retry: 3000\n\n"
        while not await request.is_disconnected():
            v = db.VERSION["n"]
            now = time.time()
            # resend at least every 10 s so online dots, idle times and time used stay fresh
            if v != last or now - last_sent > 10:
                data = await asyncio.to_thread(dashboard, section)
                last, last_sent = v, now
                yield "data: " + json.dumps(data, separators=(",", ":")) + "\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/teacher/dicts/export.csv")
def teacher_export(section: str = "", _t=Depends(teacher)):
    d = dashboard(section)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["rank", "name", "roll_no", "section", "university", "contact", "status", "xp", "cleared", "total", "stars", "first_try", "timed_out",
                "solutions_viewed", "time_used_min", "tab_switches", "copy_paste", "second_tab", "weakest_idea",
                "current_stage", "current_question", "activity", "idle_minutes", "teacher_resumes", "last_seen",
                # the end-of-mission feedback (blank until the student sends it)
                "feedback_sent", "fb_enjoyed_1_to_5", "fb_toughest_stage", "fb_favourite_stage", "fb_difficulty", "fb_time",
                "fb_confidence_1_to_5", "fb_helped_most", "fb_technical_problems", "fb_improve"])
    fb = {f["id"]: f for f in d["feedback"]["responses"]}
    for r in d["students"]:
        f = fb.get(r["id"])
        weak = min(r["concepts"].items(), key=lambda kv: kv[1]) if r["concepts"] else None
        cur = r["current"] or {}
        w.writerow([r["rank"], r["name"], r["roll_no"], r["section"], r["university"], r["contact"], r["status_label"], r["xp"], r["done"], r["total"],
                    r["stars"], r["first_try"], r["timed_out"], r["revealed"], r["used_minutes"], r["tab_switches"],
                    r["copy_paste"], r["multi_tab"],
                    f"{C.CONCEPTS.get(weak[0], weak[0])} ({round(weak[1] * 100)}%)" if weak else "",
                    cur.get("stage", ""), f"{cur['n']}/{cur['of']} {cur['title']}" if cur else "",
                    r["activity"] or "", round(r["idle_seconds"] / 60, 1) if r["activity"] else "", r["resumes"], r["last_seen"] or "",
                    *(["yes", f["enjoy"], f["toughest_label"], f["favourite_label"], f["difficulty_label"], f["pace_label"],
                       f["confidence"], "; ".join(f["helped"]), f["tech_label"], f["improve"]] if f else ["no"] + [""] * 9)])
    name = f"{C.UI['short'].lower().replace(' ', '-')}-{(section or 'all').lower().replace(' ', '-')}.csv"
    # BOM: Excel then reads the emoji and Indian names as UTF-8
    return Response("\ufeff" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})


@app.get("/api/teacher/dicts/feedback.csv")
def teacher_feedback_export(section: str = "", _t=Depends(teacher)):
    d = dashboard(section)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["name", "roll_no", "section", "university", "contact", "enjoyed_1_to_5", "toughest_stage",
                "favourite_stage", "difficulty", "time", "confidence_1_to_5", "helped_most", "technical_problems",
                "improve", "reached", "status", "sent_at"])
    for r in d["feedback"]["responses"]:
        w.writerow([r["name"], r["roll_no"], r["section"], r["university"], r["contact"], r["enjoy"], r["toughest_label"],
                    r["favourite_label"], r["difficulty_label"], r["pace_label"], r["confidence"], "; ".join(r["helped"]),
                    r["tech_label"], r["improve"], r["reached"], r["status_label"], r["at"] or ""])
    name = f"{C.UI['short'].lower().replace(' ', '-')}-feedback-{(section or 'all').lower().replace(' ', '-')}.csv"
    return Response("\ufeff" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})


@app.post("/api/teacher/dicts/{student_id}/reset")
def teacher_reset(student_id: int, _t=Depends(teacher)):
    with db.tx():
        if not db.by_id(student_id):
            raise HTTPException(404, "No such student.")
        db.reset_state(student_id, E.new_state())
    return {"ok": True}


@app.post("/api/teacher/dicts/{student_id}/resume")
def teacher_resume(student_id: int, _t=Depends(teacher)):
    """Reopen a mission that ended on tab switches or time, from where the student stopped."""
    with db.tx():
        cur = db.by_id(student_id, lock=True)
        if not cur:
            raise HTTPException(404, "No such student.")
        st = cur["state"]
        E.tick(st, RULES)
        body = E.resume(st, RULES)
        db.save_state(student_id, st, seen=False)
    return {"ok": True, "remaining": body["state"]["remaining"]}


@app.post("/api/teacher/students/{student_id}/release")
def teacher_release(student_id: int, _t=Depends(teacher)):
    with db.tx():
        if not db.by_id(student_id):
            raise HTTPException(404, "No such student.")
        db.set_token(student_id, None, seen=False)
    return {"ok": True}


@app.delete("/api/teacher/students/{student_id}")
def teacher_delete(student_id: int, _t=Depends(teacher)):
    with db.tx():
        if not db.by_id(student_id):
            raise HTTPException(404, "No such student.")
        db.delete_student(student_id)
    return {"ok": True}


# ---------- pages ----------
NO_CACHE = {"Cache-Control": "no-cache"}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html", headers=NO_CACHE)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(STATIC / "favicon.svg", media_type="image/svg+xml")


@app.get("/teacher", include_in_schema=False)
def teacher_page():
    return FileResponse(STATIC / "teacher.html", headers=NO_CACHE)


app.mount("/static", NoCacheStatic(directory=STATIC), name="static")
