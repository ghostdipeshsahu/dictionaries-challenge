# Deploy guide: two sessions on Vercel

This one repository runs two classroom practices. Each one is deployed as its **own Vercel project** with its
**own database**, so the two classes never share data and one class can never slow the other's database.

| Session | Topic | Branch to deploy | `MISSION` | Clock | Questions |
|---|---|---|---|---|---|
| Session 29 | Dictionaries (canteen board) | `session-29` | `s29` | 45 min | 27 + optional bonus round |
| Session 30 | Working with Dictionaries (Ooty trip sheet) | `session-30` | `s30` | 45 min | 28 |

Each site has a student page (`/`) and a teacher dashboard (`/teacher`). When a student's mission ends (time,
3 tab switches, or finishing), a short feedback form opens; then their report. The teacher dashboard shows every
student live and exports one CSV with progress and feedback.

## What you need

- Access to this GitHub repository.
- A Vercel account (Pro is right for company classes; Hobby is for personal, non-commercial use).
- About 10 minutes per session.

## Steps (do them once for Session 29, then again for Session 30)

1. **Create the project.** Vercel → **Add New → Project** → import this repository.
   Name it so you can tell them apart, e.g. `dictionaries-s29` and `dictionaries-s30`.
   Framework: leave as detected (FastAPI, from `app/main.py`). Root directory: the repository root.
2. **Environment variables** (on the import screen, or Settings → Environment Variables, for Production):
   - `MISSION` = `s29` (or `s30`)
   - `TEACHER_PASSWORD` = a password only the teachers know. Use a different one per project if you like.
   - Optional: `CLASS_CODE` (students must also type it), `MAX_TAB_SWITCHES` (default 3), `IDLE_SECONDS` (default 120).
3. **Deploy.**
4. **Production branch.** Settings → Git → **Production Branch** = `session-29` (or `session-30`) → Save.
   Then a change pushed for one session never redeploys the other.
5. **Database (required).** Project → **Storage → Create Database → Neon (Postgres)**.
   - Create a **new** database for each project (never share one between the two sessions: a student who
     attends both would be refused, and the data would mix).
   - Region: **US East (N. Virginia) `us-east-1`**. The app runs in Vercel's Washington region (`iad1`, set in
     `vercel.json`) and talks to the database several times per click, so the two must be close.
     If you pick another database region, change `"regions"` in `vercel.json` to the Vercel region next to it.
   - Connect it to this project for all environments. This sets `DATABASE_URL` automatically.
   Without a database the site still opens, but progress is kept in temporary memory and **will be lost**
   (the teacher dashboard shows a red warning).
6. **Redeploy** (Deployments → the latest → Redeploy), so the new database setting is used.

## Check it before giving the link to students

Open `https://<your-project>.vercel.app/api/health?db=1`. You should see:

- `"storage": "postgres"`: data is saved in the database (not `"temporary"`).
- `"mission": "s29"` (or `"s30"`): the right session.
- `"db_region": "us-east-1"` and `"round_trip_ms"` of a few milliseconds: fast clicks. Hundreds of milliseconds
  means the app and database are far apart (see step 5).

Then open `/teacher`, sign in with `TEACHER_PASSWORD`, and check the dashboard loads.

## Load test (recommended before a big class)

Simulates a class: students sign in over ~10 seconds, play with 1 to 3 seconds per step, half finish and half end
early, everyone sends feedback, and a teacher dashboard refreshes every 5 seconds. It then checks that every answer
and feedback is on the dashboard and in the CSV, and **deletes all its test students** (section `LOADTEST`).

```bash
pip install httpx
LOADTEST_TEACHER_PW=<teacher password> python scripts/load_test.py https://<your-project>.vercel.app 70
```

Run it when no real class is using the site. To test two sessions at once, run it for both sites at the same time.
Measured on the first deployment: 30 students at once, 0 errors, about 0.25 s per click, all answers and feedback saved.

## On class day

- Students open the site, type name, roll number, section, university and contact number, and start.
- Teachers watch `/teacher`: live progress, who needs attention, and **Resume** for a mission that ended early.
- After class press **Export CSV** (progress and feedback in one file). Download it after every class as a backup.
- **Reset mission** erases a student's attempt; **Remove** deletes the student. Use them only on purpose.
- Data stays in the database until someone resets or removes it, or deletes the database.

## Updating later

Changes for one session go to its branch (`session-29` or `session-30`); Vercel redeploys only that project.
Content is checked in real Python before release:

```bash
python tests/verify_content.py                 # Session 29
MISSION=s30 python tests/verify_s30.py         # Session 30
python -m pytest -q tests                      # backend (add MISSION=s30 for Session 30)
```
