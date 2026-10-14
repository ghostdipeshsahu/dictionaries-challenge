# PARITY.md — Sets → Dictionaries checklist

Source of every item: the live Sets app's public files (`/`, `/teacher`, `/openapi.json`,
`/static/css/arena.css`, `/static/css/sets.css`, `/static/css/teacher.css`, `/static/js/api.js`,
`/static/js/sets.js`, `/static/js/teacher.js`, `/static/js/py-worker.js`, `/api/health`).
No student account was created on the live app and no answers were submitted. The teacher endpoint was read
once with the password the owner gave, and only class-level numbers were printed (7 stages, 42 questions,
tab limit 3); the class had no students at that time.

Legend: `[x]` matches Sets · `[~]` deliberate change · `[ ]` not done
Evidence: **E2E** = `tests/e2e_walkthrough.py` / `tests/e2e_timers.py` in Chrome · **API** = `tests/test_api.py` ·
**PY** = `tests/verify_content.py` · **SAME** = code copied from Sets unchanged (not separately exercised) ·
**SIDE** = side-by-side screenshot + computed-style comparison with the live Sets app.

How much is shared: `arena.css` is byte-identical to Sets. `dicts.js` is `sets.js` with 187 of 1,168 lines
changed (content text, labels, Board, Dict Lab, field guide, exact output check). `dicts.css` is `sets.css` with
44 of 371 lines changed (board styles replace Venn styles). `api.js` 4 lines, `py-worker.js` 2 lines (names).

## Shell and design
- [x] `arena.css` copied unchanged: fonts Sora / DM Sans / JetBrains Mono, tokens, light + dark values, cards, buttons, drawer, animations — byte-identical; SIDE: identical computed font, size, weight, colour, background and radius on body, h2, inputs, primary button, stat chip, header
- [x] `dicts.css` extends `arena.css` the way `sets.css` does
- [x] Top bar: brand button, XP roll-up, combo "hot" at 3+, mission clock (red under 5 min), field guide, user chip, sound toggle, mission progress bar — E2E (clock running, clock red at 1-min mission), SIDE
- [x] Skip link, `prefers-reduced-motion`, focus rings, `.sr-only` live regions — SAME
- [x] Feedback drawer (correct / wrong / solution shown / time up) — E2E all four; toasts, floating +XP, confetti, sounds — SAME
- [x] Keyboard: 1–9 pick — E2E (every choice question answered with number keys); Enter checks / continues — SAME
- [~] Logo: key-and-value tag (cyan name tag → gold price card) in the Sets colours; name "Dictionaries: The Python Challenge", short "Dictionaries"; also served as the favicon (Sets has none, so it logged a 404)

## Student flow
- [x] Sign-in: name, roll number, section dropdown (same sections S-001…S-004), optional class code — E2E, SIDE
- [x] One device per roll number; teacher "Release login" frees it; same roll with another name refused — API
- [x] Duplicate-tab screen — E2E; offline screen — SAME; 30 s heartbeat signs out a released device — API (ping → 401)
- [x] Mission map: hero, Start/Continue, Lab button, big progress bar, winding trail, nodes locked / next / cleared / boss, mini bars, stars — E2E
- [x] Side rail: class leaderboard (own section), badges, concept mastery, "How it works" — E2E, API (leaderboard per section)
- [x] Rules modal: Start disabled until "I have read the rules" is ticked — E2E
- [x] Stage briefing: story (first stage), Field intel, runnable demo, tip line, count + total countdown, Start / Continue / Replay — E2E
- [x] Question screen: Map button, stage name, segment bar, counter, circular timer — E2E; timer goes red under 10 s — E2E (timers)
- [x] Half-time hint nudge — E2E (timers); hint with concept label, "Another hint" — E2E, API
- [x] "Show the solution" after 2 wrong tries — E2E, API
- [x] Time-up drawer with the answer and explanation — E2E (timers), API
- [x] Stage clear: stars, XP this run, first try, timed out, new badges — E2E (all 7 stages)
- [x] Mission report: end banner complete — E2E; end banner time — E2E (timers); proctor — API; tallies, leaderboard, badges, concept mastery, review — E2E
- [x] Profile — E2E; sign-out double tap — SAME
- [x] Field guide dialog with a dictionaries cheatsheet — E2E
- [x] Browser Back button between screens — SAME (not separately exercised)

## Rules (server-side)
- [x] One 45-minute clock from accepting the rules, keeps running, ends the mission — API, E2E (timers)
- [x] Per-question countdown fixed at first open; reopening does not reset it; expire refuses early calls — API
- [x] Tab switches recorded with duration; mission ends at 3 — API; warning modal — E2E
- [x] Copy / cut / paste / right-click recorded, second tab recorded — API; blocking in the page — SAME
- [x] Hint costs a little XP; solution after 2 wrong tries — API
- [x] XP: first try + no hint +20%; fix after a miss 60%; combo bonus from 3 in a row; a miss resets combo, never XP; replay no XP; time-up / solution no XP — API

## Question types
- [x] mcq · msq · tf · ar · fill · match · order · categorize · numeric · predict · debug · coding — all answered through their own controls in E2E; every key checked in real Python — PY (591 checks)
- [x] Coding: Pyodide 0.26.4 (same version, served locally like Sets, CDN fallback), Web Worker, 5 s timeout, samples + hidden tests, console, Run samples, Submit — E2E (all 7 challenges in real Python)
- [~] Venn build → **Board build**: name tag → price card rows, no index numbers, the matching Python line and `print(menu)` after every action — E2E (both Board builds), API (wrong order is caught)
- [~] Set Lab → **Dict Lab**: add / change / delete, duplicate key, `Tea` vs `tea`, `[ ]` vs `get()` vs `in`, `keys()/values()/items()`, live view vs `list()` copy — E2E checks each against Python's real output
- [~] Output check is exact, line by line (dicts keep insertion order); Sets compared `{...}` lines ignoring order — API (wrong order fails a hidden test)
- [~] Optimize challenge also checks the code (one `menu` dictionary, no `.index()`, no `prices` list), because equal output alone cannot prove the rewrite — API

## Backend endpoints
- [x] `GET /api/health`, `POST /api/login`, `POST /api/logout`, `GET /api/me`, `POST /api/ping` — API
- [x] `GET /api/dicts/mission`, `POST /api/dicts/start|open|expire|hint|reveal|answer|proctor`, `GET /api/dicts/review`, `GET /api/dicts/leaderboard` — same request bodies as Sets' OpenAPI schema — API
- [x] `POST /api/teacher/login`, `GET /api/teacher/dicts`, `GET /api/teacher/dicts/export.csv`, `POST /api/teacher/dicts/{id}/reset`, `POST /api/teacher/students/{id}/release`, `DELETE /api/teacher/students/{id}` — API
- [x] Keys, hidden expected output, XP, stars, badges and timers decided on the server; the mission payload carries no keys; a wrong answer does not reveal the key — API

## Teacher dashboard
- [x] Password login, section filter, Refresh, Export CSV, Sign out, Student view link — E2E (login, CSV), API (section filter)
- [x] Tiles: Students, Started, Online now, Completed, Average time used, Average cleared, Answer accuracy, Integrity flags (red) — E2E screenshot
- [x] "How far the class got", "Hardest ideas first", "Question types, hardest first" — E2E screenshot
- [x] Search, sortable columns #, Name + online dot, Roll no, Section, Status, Cleared, First try, Timed out, Solutions viewed, Time used, Tab switches, Copy/paste, Weakest idea, Last seen, Actions — E2E (values), sorting — SAME
- [x] Release login / Reset mission / Remove, each with a second tap — API; double-tap UI — SAME (kept armed across live refreshes for 8 s)
- [~] Live: server push on every change (SSE), automatic 5 s polling if the push drops; green "Live" dot — E2E (student appears, progresses and completes without a reload)
- [~] Extra column "Now on": stage + question the student is on — E2E, API; also in the CSV

## Not done / differences to know
- Per-stage question counts and the type mix of the Sets mission cannot be read without a student login, so they were designed to the same total (42 over 7 stages) and the same shape (warm-up → coding → boss).
- The question countdowns add up to 76.5 minutes (35 of them are the seven 5-minute coding challenges) against the 45-minute mission clock. Countdowns are upper limits, but a student who uses most of each one will not reach the Final Boss. Sets' own total is not visible without a student login, so this could not be matched. Tune `TIME["coding"]` in `app/content.py` if needed.
