# Deploy guide: every session on one Vercel project

One deployment runs **all** the practice sessions. Each session has its own link, its own teacher dashboard and
its own students; they share one database, where every record is tagged with its session, so data never mixes.
A student can attend several sessions with the same roll number.

| Session | Student link | Teacher dashboard |
|---|---|---|
| Working with Lists | `/working-with-lists` | `/working-with-lists/teacher` |
| Built-in Functions | `/built-in-functions` | `/built-in-functions/teacher` |
| List Methods | `/list-methods` | `/list-methods/teacher` |
| Session 29 · Dictionaries | `/dictionaries` | `/dictionaries/teacher` |
| Session 30 · Working with Dictionaries | `/working-with-dictionaries` | `/working-with-dictionaries/teacher` |

The site root (`/` and `/teacher`) runs the default session (`MISSION`, Session 29 unless set). Every dashboard
has a **Session** picker to jump to another session's dashboard. When a student's mission ends (45-minute clock,
3 tab switches, or finishing), a short feedback form opens, then their report; **Export CSV** on the dashboard gives
progress and feedback in one file.

## What you need

- Access to this GitHub repository (branch `main`).
- A Vercel account (Pro is right for company classes; Hobby is for personal, non-commercial use).
- About 10 minutes, once.

## Steps

1. **Create the project.** Vercel → **Add New → Project** → import this repository (branch `main`).
   Framework: leave as detected (FastAPI, from `app/main.py`). Root directory: the repository root.
2. **Environment variables** (Production):
   - `TEACHER_PASSWORD` = a password only the teachers know (one password for every session's dashboard).
   - Optional: `MISSION` (the session at the site root; default `s29`), `MISSIONS` (limit which sessions are offered,
     e.g. `s29,s30`), `CLASS_CODE` (students must also type it), `MAX_TAB_SWITCHES` (default 3), `IDLE_SECONDS` (default 120).
3. **Deploy.**
4. **Database (required).** Project → **Storage → Create Database → Neon (Postgres)**, region
   **US East (N. Virginia) `us-east-1`**, connected to this project for all environments (this sets `DATABASE_URL`).
   The app runs in Vercel's Washington region (`iad1`, set in `vercel.json`) and talks to the database several times per
   click, so the two must be close. If you pick another database region, change `"regions"` in `vercel.json` to the
   Vercel region next to it. Without a database the site still opens, but progress is kept in temporary memory and
   **will be lost** (the teacher dashboard shows a red warning).
5. **Redeploy** (Deployments → the latest → Redeploy), so the database setting is used.

A database that was already used by an older one-session version is upgraded automatically on start: its students
belong to the `MISSION` that deployment ran.

## Check it before giving the links to students

Open `https://<your-project>.vercel.app/api/health?db=1`. You should see:

- `"storage": "postgres"`: data is saved in the database (not `"temporary"`).
- `"missions"`: every session listed with its `slug` (the link name).
- `"db_region": "us-east-1"` and `"round_trip_ms"` of a few milliseconds: fast clicks. Hundreds of milliseconds
  means the app and database are far apart (see step 4).

Then open a session's `/teacher` link, sign in with `TEACHER_PASSWORD`, and check the dashboard loads.

## Load test (recommended before a big class)

Simulates a class on one session: students sign in over ~10 seconds, play with 1 to 3 seconds per step, half finish
and half end early, everyone sends feedback, and a teacher dashboard refreshes every 5 seconds. It then checks that
every answer and feedback is on the dashboard and in the CSV, and **deletes all its test students** (section `LOADTEST`).

```bash
pip install httpx
LOADTEST_TEACHER_PW=<teacher password> python scripts/load_test.py https://<your-project>.vercel.app/list-methods 70
```

To test several classes at once, run it for several session links at the same time. Run it when no real class is
using the site.

## On class day

- Give each section its session's link. Students type name, roll number, section, university and contact number, and start.
- Teachers watch that session's `/teacher`: live progress, who needs attention, and **Resume** for a mission that ended early.
- After class press **Export CSV**. Download it after every class as a backup.
- **Reset mission** erases a student's attempt; **Remove** deletes the student. Use them only on purpose.
- Data stays in the database until someone resets or removes it, or deletes the database.

## Adding or changing a session

A session is one file, `app/mission_<key>.py` (with `SLUG` for its link), plus its content checker
`tests/verify_<key>.py`. Push to `main` and Vercel redeploys. Content is checked in real Python before release:

```bash
python tests/verify_content.py                       # Session 29
MISSION=s30 python tests/verify_s30.py               # Session 30
MISSION=<key> python tests/verify_<key>.py           # the other sessions
python -m pytest -q tests                            # backend (MISSION=<key> to run it for another session)
```
