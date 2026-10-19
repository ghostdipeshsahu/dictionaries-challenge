# Dictionaries: The Python Challenge

A 45-minute, timed, proctored, gamified mission on Python dictionaries (Session 29, the canteen price board).
It is a twin of **Set Operations: The Python Challenge**: same screens, components, rules, backend design and
teacher dashboard. Only the content, the logo, the visual question (Board build), the free-play lab (Dict Lab)
and the live dashboard are different. See `PARITY.md` for the item-by-item checklist.

- Student app: `/`
- Teacher dashboard: `/teacher`
- API docs: `/docs`

**Deploying for a class: see [`DEPLOY.md`](DEPLOY.md)** (one Vercel project and one database per session, branches
`session-29` and `session-30`, checks, load test).

## Two missions, one codebase

| `MISSION` | Session | Story | Visual question | Lab |
|---|---|---|---|---|
| `s29` (default) | 29 · Dictionaries | the canteen price board | Board build | Dict Lab |
| `s30` | 30 · Working with Dictionaries (copy, clear, `*args`, `**kwargs`) | Divya's Ooty trip money sheet | Where does it land? | Trip Lab |

Each mission runs as its own site with its own database: set `MISSION` per deployment. Content lives in
`app/mission_s29.py` and `app/mission_s30.py`; everything else (game, rules, teacher dashboard) is shared.

### Guidance built into every mission
Students were unsure what to do, so every mission guides them step by step: a 4-card **How to play** tour,
a **Your task** box with numbered steps on every question, a **first-time card** for each new kind of question
(its timer starts only after "Got it"), a line under Check saying what is still needed, and on each briefing the
**goals** of the stage plus a **worked example** played one line at a time.

## Run locally

```bash
pip install -r requirements.txt
python scripts/vendor_pyodide.py          # optional: local copy of Python-in-the-browser (works without internet)
uvicorn app.main:app --port 8000
```

Open http://localhost:8000. The teacher password comes from `TEACHER_PASSWORD` (if it is not set, it is `change-me`,
which is only for trying it on a laptop; always set your own).

## Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `TEACHER_PASSWORD` | `change-me` | Teacher dashboard password (always set it) |
| `CLASS_CODE` | empty | If set, students must also type this code |
| `MISSION_MINUTES` | `45` | Mission clock |
| `MAX_TAB_SWITCHES` | `3` | The mission ends at this many tab switches (`0` = record only) |
| `REVEAL_AFTER` | `2` | Wrong tries before "Show the solution" appears |
| `IDLE_SECONDS` | `120` | Mission running, page open, no step for this long: flagged "idle" to the teacher |
| `MISSION` | `s29` | Which session's content this server runs (`s29` or `s30`) |
| `DATABASE_URL` | empty | Postgres URL (Vercel + Neon). When set, used instead of SQLite |
| `DB_PATH` | `data/dicts.db` | SQLite file |

## Tests

```bash
python tests/verify_content.py            # Session 29: every answer, option, solution and hidden test run in real Python
python tests/verify_s30.py                # Session 30: the same, plus every landing mapping against Python's own binder
MISSION=s30 python -m pytest -q tests     # the backend suite on Session 30 (without MISSION: Session 29)
python -m pytest -q tests                 # backend rules: login, timers, XP, combo, stars, badges, proctoring, teacher
# browser walkthroughs (need Chrome + `pip install playwright`), against a running server:
python tests/e2e_walkthrough.py http://localhost:8000 shots
MISSION_MINUTES=1 DB_PATH=data/timers.db uvicorn app.main:app --port 8011   # separate server for the clock test
python tests/e2e_timers.py http://localhost:8011 shots-timers
python tests/e2e_feedback.py http://localhost:8011 shots-feedback               # same 1-minute server: the feedback
IDLE_SECONDS=20 DB_PATH=data/scratch.db uvicorn app.main:app --port 8012           # separate server for resume + idle
python tests/e2e_resume.py http://localhost:8012 shots-resume
```
The browser tests delete the students they create when they finish.

## Teacher controls added beyond the Sets app

- **Resume** (dashboard, tap twice): reopens a mission that ended on tab switches or time, from where the student
  stopped. XP, cleared challenges, stars and badges are kept. Time spent ended is not counted, so the student gets
  back the time they had left (at least 5 minutes); the open question keeps its remaining seconds; the tab-switch
  limit starts again (the Tab switches column keeps the total). The student's page notices within 5 seconds and
  continues by itself, or the student presses **Check again**.
- **Needs attention** panel at the top of the dashboard: students who are **idle** (page open, mission running, no
  step for `IDLE_SECONDS`), **offline** (mission running, page stopped responding) or whose mission **ended** (with
  the Resume button). The "Now on" column shows the same tags.
- **Sign-in**: students type their name, roll number, section, university and contact number (all required). There
  is no fixed section list: "s-001", "S 001" and "S001" join the same section, and the dashboard's section filter
  lists the sections students actually typed. University shows under each name on the dashboard; university and
  contact are in both CSV exports.
- **Student feedback**: when a mission ends (time, tab switches, Final Boss or bonus round cleared, or Finish), a
  five-step feedback opens by itself and must be sent before the report. It asks only about the practice: enjoyment
  faces, a tomato for the toughest stage and a star for the favourite, difficulty, whether the clock was enough,
  confidence, what helped, technical problems and one thing to improve. Who sent it (name, roll, section, university,
  contact) and how far they got come from the sign-in and the app. The dashboard's **Student feedback** panel shows
  averages, counts, comments and every response; **Download feedback CSV** exports them. Asked once per attempt
  (a teacher Resume keeps it; Reset mission clears it).

## Deploy on Vercel

For Session 30, import the same repo as a **second** Vercel project, add `MISSION=s30`, and give it its own Neon database.


1. Import the GitHub repo in Vercel (FastAPI is detected from `app/main.py`). `vercel.json` runs the app in
   Washington (`iad1`), next to Neon's default region `us-east-1`: every request makes several database round trips,
   so the app must sit next to the database (Mumbai + Virginia took about 1.4 s per click; check with
   `/api/health?db=1`, which reports `db_region` and `round_trip_ms`). If the database is elsewhere, pick the
   Vercel region nearest to it.
2. **Storage → Create Database → Neon (Postgres)** and connect it to the project. This sets `DATABASE_URL`.
   Without it, the dashboard shows a red warning: Vercel's disk is temporary and progress would be lost.
3. Set `TEACHER_PASSWORD` under Settings → Environment Variables, then redeploy.

On Vercel the teacher dashboard refreshes every 5 seconds (each request may reach a different short-lived server,
so the push stream is turned off). Python for the coding challenges loads from the jsDelivr CDN.
Each change to a student runs in a transaction that locks that student's row, so parallel servers stay consistent.
Test the Postgres path locally with `python tests/run_pg.py` (needs `pip install pgserver`).

## Deploy on Render

`render.yaml` is a blueprint: Python web service, build installs requirements and downloads Pyodide, start runs
uvicorn, SQLite lives on a 1 GB persistent disk at `/var/data`. Set `TEACHER_PASSWORD` in the dashboard.
A persistent disk needs a paid instance; on the free plan the database is wiped on every restart or redeploy.
Run a single instance: state is in one SQLite file, and the live teacher feed watches that process.

## How it is built

```
app/content.py    the 42 questions, 7 stages, badges, concepts (all answer keys live here, server-side only)
app/engine.py     grading, XP, combo, stars, badges, mission + question clocks, proctoring limits
app/main.py       FastAPI routes (/api/login, /api/dicts/*, /api/teacher/*) and pages
app/db.py         SQLite: one row per student, mission state as JSON
static/           index.html, teacher.html, css/arena.css (shared base, unchanged from Sets), css/dicts.css,
                  js/dicts.js (game UI), js/teacher.js, js/api.js, js/py-worker.js (Pyodide in a Web Worker)
```

Learner code runs only in the learner's browser (Pyodide in a Web Worker, killed after 5 s). The browser sends
the printed output of every test; the server compares it with expected output it never sent. Hidden tests send
their input but not their expected output. Output is compared line by line, exactly, because dictionaries keep
insertion order.
