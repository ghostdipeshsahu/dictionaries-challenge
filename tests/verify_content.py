"""Run every expected output, reference solution and error case in real Python.

    python tests/verify_content.py

Exits non-zero on the first mismatch. Uses the same output format the client shows:
printed lines, then "!ErrorType: message" if Python stops with an error.
"""
import contextlib
import io
import itertools
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import content as C  # noqa: E402  (the active mission, see MISSION)
from app.engine import same_output, check_rules  # noqa: E402

FAILS = []
CHECKS = 0


def ok(cond, msg):
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


def run(code, stdin=""):
    """Return (stdout, error_type, error_msg, error_line, env)."""
    feed = iter(stdin.split("\n"))

    def _input(prompt=""):
        try:
            return next(feed)
        except StopIteration:
            raise EOFError("EOF when reading a line")

    env = {"__name__": "__main__", "input": _input}
    out = io.StringIO()
    err = (None, None, None)
    with contextlib.redirect_stdout(out):
        try:
            exec(compile(code, "main.py", "exec"), env)
        except BaseException as e:  # noqa: BLE001
            line = None
            tb = e.__traceback__
            while tb is not None:
                if tb.tb_frame.f_code.co_filename == "main.py":
                    line = tb.tb_lineno
                tb = tb.tb_next
            err = (type(e).__name__, str(e), line)
    return out.getvalue(), err[0], err[1], err[2], env


def shown(code, stdin=""):
    """The output exactly as an option string writes it."""
    out, et, em, _, _ = run(code, stdin)
    text = out.rstrip("\n")
    if et:
        text = (text + "\n" if text else "") + f"!{et}: {em}"
    return text


def run_expr(expr, setup=""):
    out, et, em, _, env = run(setup + "\n__r = " + expr)
    return (str(env["__r"]) if not et else None), et


Q = C.QUESTIONS

# ---------- level demos run cleanly ----------
for lvl in C.LEVELS:
    _, et, em, _, _ = run(lvl["demo"])
    ok(et is None, f"{lvl['id']} demo raised {et}: {em}")
    for qid in lvl["main"]:
        ok(qid in Q, f"{lvl['id']} lists missing question {qid}")

# ---------- choice questions with code: the marked option is what Python prints ----------
for q in Q.values():
    if q["type"] == "predict":
        code = C.BOSS_SCENARIO if q.get("scenario") else q["code"]
        actual = shown(code)
        if q.get("scenario"):
            # the scenario prints the board; B-1 asks for exactly that
            pass
        ok(q["options"][q["answer"]] == actual, f"{q['id']} answer {q['options'][q['answer']]!r} != Python {actual!r}")
        others = [o for i, o in enumerate(q["options"]) if i != q["answer"]]
        ok(actual not in others, f"{q['id']} a distractor equals the real output")
        ok(len(set(q["options"])) == len(q["options"]), f"{q['id']} duplicate options")
    if q["type"] in ("mcq", "predict", "ar", "msq"):
        for k in (q.get("why") or {}):
            ok(0 <= k < len(q["options"]) and k != q.get("answer"), f"{q['id']} why key {k} invalid")

# ---------- numeric ----------
ok(shown(Q["L1-5"]["code"]) == str(Q["L1-5"]["value"]), "L1-5 numeric")
ok(shown(Q["L4-5"]["code"]) == str(Q["L4-5"]["value"]), "L4-5 numeric")
_, _, _, _, env = run(Q["L4-5"]["code"])
ok(env["menu"] == {"tea": 14, "samosa": 15, "Tea": 16}, "L4-5 explain board")
# B-2: count updates that hit an existing key
menu = {"tea": 12, "coffee": 15, "samosa": 15}
changes = 0
for name, price in [("chai", 10), ("coffee", 18), ("samosa", 15), ("dosa", 20), ("chai", 12)]:
    changes += name in menu
    menu[name] = price
ok(changes == Q["B-2"]["value"], f"B-2 numeric {changes}")
ok("{'tea': 12, 'coffee': 18, 'samosa': 15, 'chai': 12, 'dosa': 20}" == shown(C.BOSS_SCENARIO), "BOSS scenario print")

# ---------- true / false ----------
ok(shown('print(type({"tea": 12}))') == "<class 'dict'>", "L0-2 tf")
ok(Q["L0-2"]["value"] is True, "L0-2 key")
_, _, _, _, env = run('menu = {"coffee": 15, "tea": 12}\nmenu["coffee"] = 18')
ok(list(env["menu"]) == ["coffee", "tea"] and env["menu"]["coffee"] == 18 and Q["L2-4"]["value"] is False, "L2-4 tf")

# ---------- mcq without code ----------
ok(Q["L0-3"]["options"][Q["L0-3"]["answer"]] == str(len({"tea": 12, "coffee": 15, "samosa": 15})), "L0-3")

# ---------- assertion & reason ----------
ok(shown('menu = {"tea": 12, "coffee": 15, "samosa": 15}\nprint(menu[2])') == "!KeyError: 2" and Q["L3-4"]["answer"] == 0, "L3-4 ar")

# ---------- categorize ----------
cat = Q["L1-2"]
for item, k in zip(cat["items"], cat["mapping"]):
    r, et = run_expr(f"type({item}).__name__")
    ok(et is None and ((r == "dict") == (k == 0)), f"L1-2 {item} -> {r}, keyed {cat['categories'][k]}")
cat = Q["L4-3"]
for item, k in zip(cat["items"], cat["mapping"]):
    _, et, em, _, _ = run(item)
    got = "Works" if et is None else et
    ok(got == cat["categories"][k], f"L4-3 {item} -> {got} ({em}), keyed {cat['categories'][k]}")

# ---------- match ----------
for qid, setup in (("L1-4", 'menu = {"tea": 12, "coffee": 15}'), ("L3-6", 'menu = {"coffee": 15, "samosa": 15}')):
    q = Q[qid]
    for i, expr in enumerate(q["left"]):
        r, et = run_expr(expr, setup)
        ok(r == q["right"][q["mapping"][i]], f"{qid} {expr} -> {r!r}, keyed {q['right'][q['mapping'][i]]!r}")
    ok(sorted(q["mapping"]) == list(range(len(q["right"]))), f"{qid} mapping is not one-to-one")

# ---------- fill: every accepted answer gives the target output ----------
FILL_EXPECT = {"L1-6": "12", "L3-8": "tea\ncoffee\nsamosa"}
for qid, want in FILL_EXPECT.items():
    q = Q[qid]
    parts = q["code"].split("___")
    ok(len(parts) - 1 == len(q["blanks"]), f"{qid} blank count")
    for combo in itertools.product(*q["blanks"]):
        code = parts[0] + "".join(b + p for b, p in zip(combo, parts[1:]))
        ok(shown(code) == want, f"{qid} with {combo} prints {shown(code)!r}")
# a tempting wrong fill really is wrong
ok(shown(Q["L3-8"]["code"].replace("___", "items", 1).replace("___", "<", 1)) == "tea", "L3-8 trap '<'")

# ---------- order: the key is the only order that prints the target ----------
q = Q["L2-7"]
want = "1\n{'coffee': 15, 'tea': 14}"
ok(shown("\n".join(q["items"][i] for i in q["mapping"])) == want, "L2-7 keyed order")
winners = [p for p in itertools.permutations(range(len(q["items"]))) if shown("\n".join(q["items"][i] for i in p)) == want]
ok(winners == [tuple(q["mapping"])], f"L2-7 has {len(winners)} winning orders")
ok(list(q["mapping"]) != list(range(len(q["items"]))), "L2-7 starts already solved")

# ---------- msq statements ----------
_, _, _, _, env = run('menu = {"tea": 12, "puff": 20, "maggi": 30}\ndel menu["puff"]')
m = env["menu"]
truth = [len(m) == 2, ("puff" in m) is False, m.get("puff") is None, False, (20 in m.values()) is True]
_, et, _, _, _ = run('menu = {"tea": 12, "maggi": 30}\nmenu["puff"]')
ok(et == "KeyError", "L2-5 option D really raises")
ok([i for i, t in enumerate(truth) if t] == Q["L2-5"]["answers"], f"L2-5 truth {truth}")
ok(shown('print({"b": 1, "a": 2, "c": 3})') == "{'b': 1, 'a': 2, 'c': 3}", "L4-6 insertion order holds")
ok(shown('menu = {"tea": 12}\nprint(menu[0])') == "!KeyError: 0", "L4-6 menu[0] is a key lookup")

# ---------- debug missions ----------
for qid, stdin in (("L3-7", ""), ("L4-4", "")):
    q = Q[qid]
    _, et, em, line, _ = run(q["code"], stdin)
    ok(line == q["line"], f"{qid} stops on line {line}, keyed {q['line']}")
    ok(q["errors"][q["error"]].startswith(et) and (em in q["errors"][q["error"]] or et == "KeyError"), f"{qid} error {et}: {em} vs {q['errors'][q['error']]}")
q = Q["B-6"]
out, et, _, _, env = run(q["code"], "tea dosa samosa")
ok(et is None and out.strip() == "27" and env["menu"].get("dosa") == 0 and list(env["menu"])[-1] == "dosa", "B-6 AI code: right total, dosa added at 0")
ok(q["code"].split("\n")[q["line"] - 1].strip() == "menu[item] = 0", "B-6 keyed line")

# ---------- board builds: a real sequence of taught lines reaches the target ----------
BOARD_OPS = {
    "L2-2": 'menu["tea"] = 14\nmenu["samosa"] = 15',
    "L2-6": 'del menu["puff"]\nmenu["maggi"] = 25\nmenu["coffee"] = 15',
}
for qid, ops in BOARD_OPS.items():
    q = Q[qid]
    start = dict((k, v) for k, v in q["start"])
    _, et, _, _, env = run("menu = " + repr(start) + "\n" + ops)
    ok(et is None and list(env["menu"].items()) == [tuple(r) for r in q["target"]], f"{qid} ops reach the target")
    ok(dict(q["start"]) != dict(q["target"]) or q["start"] != q["target"], f"{qid} starts solved")
# deleting then re-adding tea moves it, so the order check in L2-2 is meaningful
_, _, _, _, env = run('menu = {"tea": 12, "coffee": 15}\ndel menu["tea"]\nmenu["tea"] = 14\nmenu["samosa"] = 15')
ok(list(env["menu"]) != [r[0] for r in Q["L2-2"]["target"]], "L2-2 trap path differs")

# ---------- coding: reference passes every test, starter fails at least one or breaks a rule ----------
for q in Q.values():
    if q["type"] != "coding":
        continue
    ch = q["challenge"]
    ok(any(not t.get("hidden") for t in ch["tests"]) and any(t.get("hidden") for t in ch["tests"]), f"{q['id']} needs sample and hidden tests")
    for t in ch["tests"]:
        out, et, em, _, _ = run(q["solution"], t["stdin"])
        ok(et is None and same_output(out, t["expected"]), f"{q['id']} solution on {t['stdin']!r}: {out!r} {et} {em}")
    ok(not check_rules(q, q["solution"]), f"{q['id']} solution breaks a rule: {check_rules(q, q['solution'])}")
    starter_pass = all((lambda r: r[1] is None and same_output(r[0], t["expected"]))(run(ch["starter"], t["stdin"])) for t in ch["tests"])
    ok(not starter_pass or check_rules(q, ch["starter"]), f"{q['id']} starter already passes")
    # the starter in the Python spec must run (or fail) without a syntax error
    ok("SyntaxError" != (run(ch["starter"], ch["tests"][0]["stdin"])[1]), f"{q['id']} starter has a syntax error")

# Fix the Bill and Fix the Board Builder really crash the way the statement says
ok(run(Q["L5-5"]["challenge"]["starter"], "2\ntea 1\ndosa 3")[1] == "KeyError", "L5-5 starter KeyError")
r = run(Q["B-3"]["challenge"]["starter"], "2\ntea 12\ncoffee 15")
ok(r[1] == "ValueError" and "element #0 has length 3" in r[2], f"B-3 starter {r[1]}: {r[2]}")
ok(run(Q["L5-1"]["challenge"]["starter"].replace("# add up", "for item in order:\n    total = total + menu[item]\n# add up"), "tea dosa")[1] == "KeyError", "Task 1 crash with dosa")
# deck numbers
ok(shown(f'menu = {C.MENU}\nprint(menu["tea"] + menu["maggi"])') == "42", "deck bill 42")
ok(shown('names = ["tea", "coffee", "samosa", "puff", "maggi"]\nprices = [12, 15, 15, 20, 30]\nnames.remove("puff")\nprint(prices[names.index("tea")] + prices[names.index("maggi")])') == "32", "deck bill 32")

# ---------- metadata ----------
LEVELS_OK = {"Recall", "Read", "Implement", "Debug", "Extend", "Optimize", "Prompting"}
for q in Q.values():
    ok(q["level"] in LEVELS_OK, f"{q['id']} level {q['level']}")
    ok(q["concept"] in C.CONCEPTS, f"{q['id']} concept {q['concept']}")
    ok(q["type"] in C.TYPE_LABEL, f"{q['id']} type")
    ok(bool(q.get("hints")) and bool(q.get("explain")), f"{q['id']} needs hints and explain")
ok(set(q["level"] for q in Q.values()) == LEVELS_OK, "every cognitive level used")
ok(set(q["concept"] for q in Q.values()) == set(C.CONCEPTS), f"unused concepts {set(C.CONCEPTS) - set(q['concept'] for q in Q.values())}")
ok(set(q["type"] for q in Q.values()) == set(C.TYPE_LABEL), "every question type used")

# words the deck does not teach must not appear in content shown to students
BANNED = [r"\.pop\(", r"\.update\(", r"setdefault", r"\.copy\(", r"\bunordered\b(?!.*not)"]
for q in Q.values():
    blob = repr({k: v for k, v in q.items() if k not in ("why", "trap", "explain")})
    for pat in BANNED[:4]:
        ok(not re.search(pat, blob), f"{q['id']} uses untaught {pat}")

print(f"\n{CHECKS} checks, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
