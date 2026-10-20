"""Run every Session 30 answer, option, worked example, landing mapping and coding test in real Python.

    MISSION=s30 python tests/verify_s30.py      (MISSION is set here if missing)
"""
import contextlib
import inspect
import io
import itertools
import os
import re
import sys

os.environ.setdefault("MISSION", "s30")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import mission_s30 as C  # noqa: E402
from app.engine import check_rules, same_output  # noqa: E402

FAILS, N = [], [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


def run(code, stdin=""):
    feed = iter(stdin.split("\n"))

    def _input(prompt=""):
        try:
            return next(feed)
        except StopIteration:
            raise EOFError("EOF when reading a line")

    env = {"__name__": "__main__", "input": _input}
    out, err = io.StringIO(), (None, None, None)
    with contextlib.redirect_stdout(out):
        try:
            exec(compile(code, "main.py", "exec"), env)
        except BaseException as e:  # noqa: BLE001
            line, tb = None, e.__traceback__
            while tb is not None:
                if tb.tb_frame.f_code.co_filename == "main.py":
                    line = tb.tb_lineno
                tb = tb.tb_next
            err = (type(e).__name__, str(e), line)
    return out.getvalue(), err[0], err[1], err[2], env


def shown(code, stdin=""):
    out, et, em, _, _ = run(code, stdin)
    text = out.rstrip("\n")
    if et:
        text = (text + "\n" if text else "") + f"!{et}: {em}"
    return text


Q = C.QUESTIONS

# ---------- demos and worked examples: what the steps show is exactly what Python prints ----------
for lvl in C.LEVELS:
    out, et, em, _, _ = run(lvl["demo"])
    ok(et is None, f"{lvl['id']} demo raised {et}: {em}")
    shows = [w["shows"] for w in lvl["walk"] if "shows" in w]
    ok("\n".join(shows) == out.rstrip("\n"), f"{lvl['id']} walk shows {shows!r} but Python prints {out!r}")
    nlines = len(lvl["demo"].split("\n"))
    ok(all(1 <= w["line"] <= nlines and lvl["demo"].split("\n")[w["line"] - 1].strip() for w in lvl["walk"]), f"{lvl['id']} walk points at a blank or missing line")
    ok(bool(lvl.get("learn")), f"{lvl['id']} needs learning goals")

# ---------- predict: the keyed option is Python's output, no distractor equals it ----------
for q in Q.values():
    if q["type"] == "predict":
        actual = shown(C.BOSS_SCENARIO if q.get("scenario") else q["code"])
        ok(q["options"][q["answer"]] == actual, f"{q['id']} keyed {q['options'][q['answer']]!r} != Python {actual!r}")
        ok(actual not in [o for i, o in enumerate(q["options"]) if i != q["answer"]], f"{q['id']} a distractor equals the output")
        ok(len(set(q["options"])) == len(q["options"]), f"{q['id']} duplicate options")
    if q["type"] in ("mcq", "predict", "ar", "msq"):
        for k in q.get("why") or {}:
            ok(0 <= k < len(q["options"]) and k != q.get("answer"), f"{q['id']} why key {k}")

# ---------- numeric ----------
for qid in ("L1-3",):
    ok(shown(Q[qid]["code"]) == str(Q[qid]["value"]), f"{qid} numeric {shown(Q[qid]['code'])!r}")
_, _, _, _, env = run(C.BOSS_SCENARIO)
ok(len({id(env["trip"]), id(env["backup"]), id(env["alias"])}) == 2, "scenario: three names, two dictionaries")

# ---------- true / false ----------
_, _, _, _, env = run(f'trip = {C.TRIP}\nravi = trip')
ok(env["trip"] is env["ravi"], "= gives a second name, not a copy")
_, _, _, _, env = run(f'trip = {C.TRIP}\nkiran = trip.copy()\nkiran["Kiran"] = 2000')
ok((env["trip"]["Kiran"] == 0) == Q["L0-2"]["value"], "L0-2 tf (a copy keeps the original)")

# ---------- ar ----------
ok(shown('def show(*friends):\n    print(friends)\nshow("Sai")') == "('Sai',)" and Q["L3-7"]["answer"] == 0, "L3-7 ar")

# ---------- fill: every accepted answer gives the expected output ----------
for q in Q.values():
    if q["type"] == "fill":
        parts = q["code"].split("___")
        ok(len(parts) - 1 == len(q["blanks"]), f"{q['id']} blank count")
        for combo in itertools.product(*q["blanks"]):
            code = parts[0] + "".join(b + p for b, p in zip(combo, parts[1:]))
            ok(shown(code) == q["expect"], f"{q['id']} with {combo} prints {shown(code)!r}")

# ---------- order: the keyed order is the only one that prints the target ----------
q = Q["L1-5"]
ok(shown("\n".join(q["items"][i] for i in q["mapping"])) == q["expect"], "L1-5 keyed order")
wins = [pm for pm in itertools.permutations(range(len(q["items"]))) if shown("\n".join(q["items"][i] for i in pm)) == q["expect"]]
ok(wins == [tuple(q["mapping"])], f"L1-5 has {len(wins)} winning orders")

# ---------- categorize: what print(backup) shows after each line ----------
q = Q["L2-3"]
for item, k in zip(q["items"], q["mapping"]):
    got = shown(q["setup"] + "\n" + item + "\nprint(backup)")
    ok(got == q["categories"][k], f"L2-3 {item} -> {got!r}, keyed {q['categories'][k]!r}")

# ---------- match ----------
q = Q["L2-6"]
for i, expr in enumerate(q["left"]):
    got = shown(q["setup"] + f"\nprint({expr})")
    ok(got == q["right"][q["mapping"][i]], f"L2-6 {expr} -> {got!r}, keyed {q['right'][q['mapping'][i]]!r}")
ok(sorted(q["mapping"]) == list(range(len(q["right"]))) and q["code"] == q["setup"], "L2-6 mapping one-to-one, code shown = code checked")

# ---------- msq ----------
q = Q["L2-4"]
truth = [shown(f"trip = {C.TRIP}\n" + o) == "True" for o in q["options"]]
ok([i for i, t in enumerate(truth) if t] == q["answers"], f"L2-4 truth {truth}")

# ---------- debug missions ----------
for qid in ("L2-7",):
    q = Q[qid]
    _, et, em, line, _ = run(q["code"])
    ok(line == q["line"], f"{qid} stops on line {line}, keyed {q['line']}")
    ok(q["errors"][q["error"]] == f"{et}: {em}", f"{qid} error {et}: {em!r} vs {q['errors'][q['error']]!r}")


# ---------- where does it land: my landing rules agree with Python's own argument binding ----------
def split_args(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


for q in Q.values():
    if q["type"] != "land":
        continue
    lines = q["code"].split("\n")
    call = lines[-1]
    fname = call[:call.index("(")]
    _, _, _, _, env = run("\n".join(lines[:-1]))
    fn = env[fname]
    params = inspect.signature(fn).parameters.values()
    named = [p.name for p in params if p.kind == p.POSITIONAL_OR_KEYWORD]
    star = next((p.name for p in params if p.kind == p.VAR_POSITIONAL), None)
    dstar = next((p.name for p in params if p.kind == p.VAR_KEYWORD), None)
    labels = named + ([f"*{star}"] if star else []) + ([f"**{dstar}"] if dstar else [])
    ok(labels == q["boxes"], f"{q['id']} boxes {q['boxes']} vs signature {labels}")
    args = split_args(call[call.index("(") + 1:-1])
    ok(args == q["args"], f"{q['id']} args {q['args']} vs call {args}")
    nobox, mapping, pos_i = len(labels), [], 0
    pos, kw = [], {}
    for a in args:
        m = re.match(r"^(\w+)=(.*)$", a)
        if m:
            kw[m.group(1)] = eval(m.group(2))
            name = m.group(1)
            mapping.append(labels.index(name) if name in named else labels.index(f"**{dstar}") if dstar else nobox)
        else:
            pos.append(eval(a))
            mapping.append(pos_i if pos_i < len(named) else labels.index(f"*{star}") if star else nobox)
            pos_i += 1
    ok(mapping == q["mapping"], f"{q['id']} rules give {mapping}, keyed {q['mapping']}")
    try:
        inspect.signature(fn).bind(*pos, **kw)
        binds = True
    except TypeError:
        binds = False
    ok(binds == (nobox not in q["mapping"]), f"{q['id']} Python binds={binds} but key says no-box={nobox in q['mapping']}")
    ok(shown(q["code"]) == q["prints"], f"{q['id']} prints {shown(q['code'])!r}, keyed {q['prints']!r}")

# ---------- coding: reference passes every test; the starter fails one or breaks a rule ----------
for q in Q.values():
    if q["type"] != "coding":
        continue
    ch = q["challenge"]
    ok(any(not t.get("hidden") for t in ch["tests"]) and any(t.get("hidden") for t in ch["tests"]), f"{q['id']} sample + hidden")
    for t in ch["tests"]:
        out, et, em, _, _ = run(q["solution"], t["stdin"])
        ok(et is None and same_output(out, t["expected"]), f"{q['id']} solution on {t['stdin']!r}: {out!r} {et} {em}")
    ok(not check_rules(q, q["solution"]), f"{q['id']} solution breaks a rule: {check_rules(q, q['solution'])}")
    starter_pass = all((lambda r: r[1] is None and same_output(r[0], t["expected"]))(run(ch["starter"], t["stdin"])) for t in ch["tests"])
    ok(not starter_pass or check_rules(q, ch["starter"]), f"{q['id']} starter already passes")
# the starters fail the way their statements say
r = run(Q["L5-4"]["challenge"]["starter"], "1\nTeja 1500")
ok(r[1] == "TypeError" and "takes 0 positional arguments but 1 was given" in r[2], f"L5-4 starter {r[1]}: {r[2]}")

# ---------- deck numbers ----------
ok(shown(f'trip = {C.TRIP}\nb = trip\nb["Kiran"] = 500\nprint(trip["Kiran"])') == "500", "deck example 1")
ok(shown(f'trip = {C.TRIP}\nb = trip.copy()\nb["Kiran"] = 500\nprint(trip["Kiran"])') == "0", "deck example 2")
ok(shown(f'trip = {C.TRIP}\ntrip.clear()\nprint(trip, len(trip))') == "{} 0", "deck example 3")
ok(shown('def room(name, block):\n    print(name, block)\nroom(**{"block": "C", "name": "Teja"})') == "Teja C", "deck example 6")

# ---------- metadata ----------
LEVELS_OK = {"Recall", "Read", "Implement", "Debug", "Extend", "Optimize", "Prompting"}
for q in Q.values():
    ok(q["level"] in LEVELS_OK and q["concept"] in C.CONCEPTS and q["type"] in C.TYPE_LABEL, f"{q['id']} metadata")
    ok(bool(q.get("hints")) and bool(q.get("explain")), f"{q['id']} hints/explain")
    blob = repr({k: v for k, v in q.items() if k not in ("why", "trap", "explain")})
    for pat in (r"\.pop\(", r"\.update\(", r"setdefault", r"lambda", r"\bdeepcopy\b"):
        ok(not re.search(pat, blob), f"{q['id']} uses untaught {pat}")
ok({q["level"] for q in Q.values()} == LEVELS_OK, "every cognitive level used")
ok({q["concept"] for q in Q.values()} == set(C.CONCEPTS), f"unused concepts {set(C.CONCEPTS) - {q['concept'] for q in Q.values()}}")
ok({q["type"] for q in Q.values()} == set(C.TYPE_LABEL), f"unused types {set(C.TYPE_LABEL) - {q['type'] for q in Q.values()}}")
ok(sum(q["type"] == "coding" for q in Q.values()) == 2, "two coding challenges")
# Timers are sized per question (base + per line of code, with a floor); the 45-minute clock is the hard stop.
ok(C.MISSION_MINUTES == 45, "45-minute mission")
for q in Q.values():
    ok(q["time"] == C.timer(q) and q["time"] >= C.FLOOR.get(q["type"], 0), f"{q['id']} timer {q['time']} s")
ok(all(q["time"] == 360 for q in Q.values() if q["type"] == "coding"), "coding gets 6 minutes")
worst = sum(q["time"] for q in Q.values())
ok(worst <= 38 * 60, f"every timer used in full is {worst / 60:.1f} min: it fits the 45-minute clock, with time to read each stage")

print(f"\n{N[0]} checks, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
