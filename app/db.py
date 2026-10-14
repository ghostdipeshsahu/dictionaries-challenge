"""SQLite storage. One row per student; mission state is a JSON column (small, read whole, written whole)."""
import json
import os
import sqlite3
import threading
import time

LOCK = threading.RLock()
_conn = None
VERSION = {"n": 0}  # bumped on every write; the teacher stream pushes when it changes


def connect(path):
    global _conn
    if path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    _conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA journal_mode=WAL" if path != ":memory:" else "PRAGMA journal_mode=MEMORY")
    _conn.executescript("""
    CREATE TABLE IF NOT EXISTS students(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL, roll_no TEXT NOT NULL, roll_key TEXT NOT NULL UNIQUE, section TEXT NOT NULL,
      token TEXT UNIQUE, created_at REAL NOT NULL, last_seen REAL, state TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS events(
      id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL, kind TEXT NOT NULL,
      qid TEXT, duration_ms INTEGER, ts REAL NOT NULL);
    CREATE INDEX IF NOT EXISTS ev_student ON events(student_id);
    CREATE TABLE IF NOT EXISTS teacher_tokens(token TEXT PRIMARY KEY, created_at REAL NOT NULL);
    """)
    return _conn


def bump():
    VERSION["n"] += 1


def roll_key(roll):
    return " ".join(str(roll).split()).upper()


def row_to_student(r):
    if not r:
        return None
    d = dict(r)
    d["state"] = json.loads(d["state"])
    return d


def by_token(token):
    if not token:
        return None
    return row_to_student(_conn.execute("SELECT * FROM students WHERE token=?", (token,)).fetchone())


def by_roll(roll):
    return row_to_student(_conn.execute("SELECT * FROM students WHERE roll_key=?", (roll_key(roll),)).fetchone())


def by_id(sid):
    return row_to_student(_conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone())


def all_students(section=None):
    if section:
        rows = _conn.execute("SELECT * FROM students WHERE section=? ORDER BY id", (section,)).fetchall()
    else:
        rows = _conn.execute("SELECT * FROM students ORDER BY id").fetchall()
    return [row_to_student(r) for r in rows]


def insert_student(name, roll, section, token, state):
    now = time.time()
    cur = _conn.execute(
        "INSERT INTO students(name, roll_no, roll_key, section, token, created_at, last_seen, state) VALUES(?,?,?,?,?,?,?,?)",
        (name, roll, roll_key(roll), section, token, now, now, json.dumps(state)))
    bump()
    return cur.lastrowid


def set_token(sid, token, seen=True):
    _conn.execute("UPDATE students SET token=?, last_seen=? WHERE id=?", (token, time.time() if seen else None, sid))
    bump()


def touch(sid):
    _conn.execute("UPDATE students SET last_seen=? WHERE id=?", (time.time(), sid))
    bump()


def save_state(sid, state):
    _conn.execute("UPDATE students SET state=?, last_seen=? WHERE id=?", (json.dumps(state), time.time(), sid))
    bump()


def reset_state(sid, state):
    _conn.execute("UPDATE students SET state=? WHERE id=?", (json.dumps(state), sid))
    _conn.execute("DELETE FROM events WHERE student_id=?", (sid,))
    bump()


def delete_student(sid):
    _conn.execute("DELETE FROM students WHERE id=?", (sid,))
    _conn.execute("DELETE FROM events WHERE student_id=?", (sid,))
    bump()


def log_event(sid, kind, qid=None, duration_ms=None):
    _conn.execute("INSERT INTO events(student_id, kind, qid, duration_ms, ts) VALUES(?,?,?,?,?)",
                  (sid, kind, qid, duration_ms, time.time()))


def add_teacher_token(token):
    _conn.execute("INSERT INTO teacher_tokens(token, created_at) VALUES(?,?)", (token, time.time()))


def teacher_token_ok(token, max_age):
    if not token:
        return False
    r = _conn.execute("SELECT created_at FROM teacher_tokens WHERE token=?", (token,)).fetchone()
    return bool(r) and time.time() - r["created_at"] < max_age


def drop_teacher_token(token):
    _conn.execute("DELETE FROM teacher_tokens WHERE token=?", (token,))
