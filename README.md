# Dictionaries: The Python Challenge

A 45-minute, timed, proctored, gamified mission on Python dictionaries (Session 29, the canteen price board).
It is a twin of **Set Operations: The Python Challenge**: same screens, components, rules, backend design and
teacher dashboard. Only the content, the logo, the visual question (Board build), the free-play lab (Dict Lab)
and the live dashboard are different. See `PARITY.md` for the item-by-item checklist.

- Student app: `/`
- Teacher dashboard: `/teacher`
- API docs: `/docs`

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
| `SECTIONS` | `S-001,S-002,S-003,S-004` | Sections in the sign-in dropdown (same as Sets) |
| `CLASS_CODE` | empty | If set, students must also type this code |
| `MISSION_MINUTES` | `45` | Mission clock |
| `MAX_TAB_SWITCHES` | `3` | The mission ends at this many tab switches (`0` = record only) |
| `REVEAL_AFTER` | `2` | Wrong tries before "Show the solution" appears |
| `IDLE_SECONDS` | `120` | Mission running, page open, no step for this long: flagged "idle" to the teacher |
| `DB_PATH` | `data/dicts.db` | SQLite file |

## Tests

```bash
python tests/verify_content.py            # every answer, option, solution and hidden test run in real Python
python -m pytest -q tests                 # backend rules: login, timers, XP, combo, stars, badges, proctoring, teacher
# browser walkthroughs (need Chrome + `pip install playwright`), against a running server:
python tests/e2e_walkthrough.py http://localhost:8000 shots
MISSION_MINUTES=1 DB_PATH=data/timers.db uvicorn app.main:app --port 8011   # separate server for the clock test
python tests/e2e_timers.py http://localhost:8011 shots-timers
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
