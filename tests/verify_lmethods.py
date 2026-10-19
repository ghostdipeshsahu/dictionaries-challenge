"""Run every List Methods answer, option, worked example, mapping and coding test in real Python.

    MISSION=lmethods python tests/verify_lmethods.py      (MISSION is set here if missing)
"""
import contextlib
import io
import itertools
import os
import re
import sys

os.environ.setdefault("MISSION", "lmethods")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import mission_lmethods as C  # noqa: E402
from app.engine import check_rules, public_question, same_output  # noqa: E402

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


def passes(code, tests):
    return all((lambda r: r[1] is None and same_output(r[0], t["expected"]))(run(code, t["stdin"])) for t in tests)


Q = C.QUESTIONS
TEAM = C.TEAM

# ---------- demos and worked examples: what the steps show is exactly what Python prints ----------
for lvl in C.LEVELS:
    out, et, em, _, _ = run(lvl["demo"])
    ok(et is None, f"{lvl['id']} demo raised {et}: {em}")
    shows = [w["shows"] for w in lvl["walk"] if "shows" in w]
    ok("\n".join(shows) == out.rstrip("\n"), f"{lvl['id']} walk shows {shows!r} but Python prints {out!r}")
    nlines = len(lvl["demo"].split("\n"))
    ok(all(1 <= w["line"] <= nlines and lvl["demo"].split("\n")[w["line"] - 1].strip() for w in lvl["walk"]), f"{lvl['id']} walk points at a blank or missing line")
    ok([w["line"] for w in lvl["walk"]] == sorted(w["line"] for w in lvl["walk"]), f"{lvl['id']} walk goes backwards")
    for k in ("name", "difficulty", "job", "intel_title", "intel", "demo", "main"):
        ok(bool(lvl.get(k)), f"{lvl['id']} needs {k}")
    ok(bool(lvl.get("learn")), f"{lvl['id']} needs learning goals")
ok([l["id"] for l in C.LEVELS] == ["L0", "L1", "L2", "L3", "L4", "L5", "BOSS"], "seven stages, L0 to BOSS")
ok(not any(l.get("bonus") for l in C.LEVELS), "no bonus round")
ok("Your 3 jobs" in C.UI["story"], "L0 story has Your 3 jobs")

# ---------- predict: the keyed option is Python's output, no distractor equals it ----------
for q in Q.values():
    if q["type"] == "predict":
        actual = shown(C.BOSS_SCENARIO if q.get("scenario") else q["code"])
        ok(q["options"][q["answer"]] == actual, f"{q['id']} keyed {q['options'][q['answer']]!r} != Python {actual!r}")
        ok(actual not in [o for i, o in enumerate(q["options"]) if i != q["answer"]], f"{q['id']} a distractor equals the output")
        ok(len(set(q["options"])) == len(q["options"]), f"{q['id']} duplicate options")
        if q.get("scenario"):
            ok(q.get("code", C.BOSS_SCENARIO) == C.BOSS_SCENARIO, f"{q['id']} code shown = the scenario")
    if q["type"] in ("mcq", "predict", "ar", "msq"):
        for k in q.get("why") or {}:
            ok(0 <= k < len(q["options"]) and k != q.get("answer"), f"{q['id']} why key {k}")
        if q["type"] in ("mcq", "predict", "ar"):
            missing = [i for i in range(len(q["options"])) if i != q["answer"] and i not in (q.get("why") or {})]
            ok(not missing, f"{q['id']} wrong options without a why: {missing}")

# the B-1 distractors are the outputs of real misreadings (each one runs and prints that option)
B1_MISREAD = {
    1: C.BOSS_SCENARIO.replace("gate = sorted(team)", "team.sort()\ngate = team"),          # sorted() sorts team
    2: C.BOSS_SCENARIO.replace("gone = team.pop()", "gone = team[0]\ndel team[0]"),       # pop() takes the first item
    3: C.BOSS_SCENARIO.replace("team.extend(late)", "team.append(late)"),                 # extend() nests like append()
}
for i, code in B1_MISREAD.items():
    ok(shown(code) == Q["B-1"]["options"][i], f"B-1 option {i} is not the output of its misreading: {shown(code)!r}")
# so are the L1-1 and L4-2 distractors
ok(shown(Q["L1-1"]["code"].replace(".append(", ".extend(")) == Q["L1-1"]["options"][1], "L1-1 option 1 is extend's output")
ok(shown('team = ["Ravi", "Anu"]\nteam.append("Sai", "Meena")') == Q["L1-1"]["options"][3], "L1-1 option 3 is the real two-argument error")
ok(shown('hours = [5, 2, 4]\nprint(sorted(hours))\nhours.sort()\nprint(hours)') == Q["L4-2"]["options"][1], "L4-2 option 1 is what sorted() would print")
ok(shown('team = ["Ravi", "Anu", "Kiran", "Anu"]\nteam.remove("Sai")') == Q["L2-1"]["options"][3], "L2-1 option 3 is the real remove() error")
ok(shown('shifts = ["Ravi"]\nprint(3)\nshifts.index("Sai")') == Q["L3-2"]["options"][2], "L3-2 option 2 is the real index() error")
ok(shown(f'team = {TEAM}\nprint(sorted(team))') == Q["L4-1"]["options"][1], "L4-1 option 1 is sorted()'s output")
ok(shown(f'team = {TEAM}\nprint(sorted(team, reverse=True))') == Q["L4-1"]["options"][3], "L4-1 option 3 is Z to A")

# ---------- mcq ----------
q = Q["L0-1"]
ok(q["answer"] == 0, "L0-1 keyed 0 (generic tests)")
ok(shown(f'team = {TEAM}\nteam.append("Sai")\nprint(team[-1], team[0], len(team))') == "Sai Ravi 4", "L0-1 append adds at the end")
ok(shown(f'team = {TEAM}\nprint(team.append("Sai"))') == "None", "L0-1 append prints nothing itself and gives back None")
q = Q["L1-3"]
want = ['Ravi', 'Divya', 'Anu', 'Kiran']
for i, opt in enumerate(q["options"]):
    out, et, em, _, env = run(f"team = {TEAM}\n{opt}")
    right_one = et is None and env["team"] == want
    ok(right_one == (i == q["answer"]), f"L1-3 option {i} {opt!r} -> {et or env['team']}")
_, et, em, _, _ = run(f"team = {TEAM}\n{q['options'][2]}")
ok(et == "TypeError", f"L1-3 insert(value, index) raises {et}")
_, _, _, _, env = run(f"team = {TEAM}\n{q['options'][3]}")
ok("Anu" not in env["team"], "L1-3 team[1] = ... loses Anu")
_, _, _, _, env = run(f"team = {TEAM}\n{q['options'][1]}")
ok(env["team"].index("Divya") == 2, "L1-3 insert(2, ...) makes Divya third")

# ---------- true / false ----------
q = Q["L0-2"]
ok(q["value"] is True, "L0-2 is True (generic tests)")
out, et, _, _, env = run(f'team = {TEAM}\nbefore = id(team)\nteam.append("Sai")\nsame = id(team) == before')
ok(et is None and env["same"] and "Sai" in env["team"], "L0-2 append changes the same list")
q = Q["L1-4"]
out, et, _, _, env = run('team = ["Ravi", "Anu"]\nteam.insert(10, "Divya")')
ok((et == "IndexError") == q["value"] and env["team"] == ['Ravi', 'Anu', 'Divya'], f"L1-4 insert past the end: {et}")
_, et, _, _, _ = run('team = ["Ravi", "Anu"]\nteam[10]')
ok(et == "IndexError", "L1-4 explanation: team[10] itself does fail")

# ---------- ar ----------
q = Q["L3-5"]
_, et, _, _, env = run('queue = ["Anu", "Ravi"]\nn = queue.count("Sai")')
a_true = et is None and env["n"] == 0
r_true = et == "ValueError"
expected = 0 if a_true and r_true else 2 if a_true and not r_true else 3 if r_true else None
ok(q["answer"] == expected, f"L3-5 ar keyed {q['answer']}, A={a_true} R={r_true}")
ok(q["options"] == C.AR_OPTIONS, "L3-5 uses AR_OPTIONS")

# ---------- numeric ----------
for q in Q.values():
    if q["type"] == "numeric":
        ok(shown(q["code"]) == str(q["value"]), f"{q['id']} numeric {shown(q['code'])!r} vs {q['value']}")
# L5-2: the deck's two fixes of the Daily Challenge both give the expected 10
code = Q["L5-2"]["code"]
ok(shown(code.replace("return 1\n", "return 0\n", 1)) == "10", "L5-2 fix 1: return 0")
ok(shown(code.replace("if n == 0:", "if n == 1:")) == "10", "L5-2 fix 2: stop at 1")
ok(shown("def sum_of_numbers(n):\n    return n + sum_of_numbers(n - 1)\nsum_of_numbers(3)").startswith("!RecursionError"), "deck: no base case -> RecursionError")
ok(shown("def multiply(n):\n    if n == 1:\n        return 1\n    return n * multiply(n - 1)\nprint(multiply(5))") == "120", "deck: multiply(5)")

# ---------- fill: every accepted answer gives the expected output, the classic wrong word does not ----------
FILL_WRONG = {"L1-2": ["append", "insert"], "L2-2": ["remove", "clear", "sort"]}
for q in Q.values():
    if q["type"] == "fill":
        parts = q["code"].split("___")
        ok(len(parts) - 1 == len(q["blanks"]), f"{q['id']} blank count")
        for combo in itertools.product(*q["blanks"]):
            code = parts[0] + "".join(b + p for b, p in zip(combo, parts[1:]))
            ok(shown(code) == q["expect"], f"{q['id']} with {combo} prints {shown(code)!r}")
        for w in FILL_WRONG[q["id"]]:
            code = parts[0] + w + parts[1]
            ok(shown(code) != q["expect"], f"{q['id']} wrong word {w} also prints the target")
ok(set(FILL_WRONG) == {q["id"] for q in Q.values() if q["type"] == "fill"}, "every fill has its wrong words checked")

# ---------- order: the keyed order is the only one that prints the target ----------
for q in Q.values():
    if q["type"] != "order":
        continue
    ok(shown("\n".join(q["items"][i] for i in q["mapping"])) == q["expect"], f"{q['id']} keyed order")
    wins = [pm for pm in itertools.permutations(range(len(q["items"]))) if shown("\n".join(q["items"][i] for i in pm)) == q["expect"]]
    ok(wins == [tuple(q["mapping"])], f"{q['id']} has {len(wins)} winning orders")
    ok(len(set(q["items"])) == len(q["items"]), f"{q['id']} duplicate lines")
    ok(q["title"].count("Divya 4") == 1 and "['Ravi', 'Anu', 'Sai']" in q["title"], f"{q['id']} title states the target")

# ---------- categorize ----------
q = Q["L2-4"]
start_len = len(eval(TEAM))
for item, k in zip(q["items"], q["mapping"]):
    _, et, _, _, env = run(q["setup"] + "\n" + item.replace("; ", "\n"))
    got = 2 if et else 1 if env["team"] == [] else 0 if len(env["team"]) == start_len - 1 else None
    ok(got == k, f"L2-4 {item} -> {got} ({et}), keyed {k}")
_, et, _, _, _ = run(q["setup"] + "\nteam.clear()\nteam.pop()")
ok(et == "IndexError", "L2-4 pop on empty -> IndexError")
_, et, _, _, _ = run(q["setup"] + '\nteam.remove("anu")')
ok(et == "ValueError", "L2-4 remove('anu') -> ValueError")
q = Q["L4-4"]
KIND = {type(None): 0, list: 1, str: 2, int: 3}
for item, k in zip(q["items"], q["mapping"]):
    _, et, _, _, env = run(q["setup"] + "\n" + item)
    ok(et is None and KIND.get(type(env["x"])) == k, f"L4-4 {item} -> {type(env.get('x')).__name__}, keyed {q['categories'][k]}")
    if k == 1:
        ok(env["x"] is not env["team"], f"L4-4 {item} is a new list")
for q in Q.values():
    if q["type"] == "categorize":
        ok(set(q["mapping"]) == set(range(len(q["categories"]))), f"{q['id']} every group used")

# ---------- match ----------
q = Q["L4-3"]
for i, expr in enumerate(q["left"]):
    got = shown(q["setup"] + f"\nprint({expr})")
    ok(got == q["right"][q["mapping"][i]], f"L4-3 {expr} -> {got!r}, keyed {q['right'][q['mapping'][i]]!r}")
ok(sorted(q["mapping"]) == list(range(len(q["right"]))) and q["code"] == q["setup"], "L4-3 mapping one-to-one, code shown = code checked")
ok(len(set(q["right"])) == len(q["right"]), "L4-3 right column has no repeats")

# ---------- msq ----------
q = Q["L3-4"]
setup = 'queue = ["Anu", "Ravi", "Kiran", "Ravi"]'
ok(setup in q["title"], "L3-4 title shows the setup")
truth = [shown(setup + "\n" + o) == "1" for o in q["options"]]
ok([i for i, t in enumerate(truth) if t] == q["answers"], f"L3-4 truth {truth}")
q = Q["B-3"]
# a reference function that meets the spec's lines 0-3 does what the example says, and line 5 would break the order
ref = 'def add_volunteer(team, name):\n    if name not in team:\n        team.append(name)\n'
ok(shown(ref + 'team = ["Ravi"]\nadd_volunteer(team, "Anu")\nprint(team)') == "['Ravi', 'Anu']", "B-3 example in the spec is right")
ok(shown(ref + 'team = ["Ravi"]\nadd_volunteer(team, "Ravi")\nprint(team)') == "['Ravi']", "B-3 edge case: no repeat")
ok(shown(ref.replace("team.append(name)", "team.append(name)\n        team.sort()") + 'team = ["Ravi"]\nadd_volunteer(team, "Anu")\nprint(team)') != "['Ravi', 'Anu']", "B-3 sorting breaks the sign-up order")
ok(q["answers"] == [0, 1, 2, 3], "B-3 keyed spec lines")

# ---------- debug missions ----------
for qid in ("L2-3", "L3-3"):
    q = Q[qid]
    _, et, em, line, _ = run(q["code"])
    ok(line == q["line"], f"{qid} stops on line {line}, keyed {q['line']}")
    ok(q["errors"][q["error"]] == f"{et}: {em}", f"{qid} error {et}: {em!r} vs {q['errors'][q['error']]!r}")
    ok(q["focus"] == q["line"], f"{qid} focus")
ok(shown(Q["L2-3"]["code"].replace('team.remove("Sai")', 'if "Sai" in team:\n    team.remove("Sai")')) == "['Ravi', 'Anu', 'Kiran', 'Meena']", "L2-3 the in-check fix works")
ok(shown(Q["L3-3"]["code"].replace("place = queue.index(name)\n", "if name in queue:\n    place = queue.index(name)\nelse:\n    place = -1\n")) == "Sai is at -1", "L3-3 the in-check fix works")
q = Q["B-4"]
_, et, em, line, _ = run(q["code"])
ok(f"{et}: {em}" == q["errors"][q["error"]], f"B-4 error {et}: {em}")
ok(line == 3, f"B-4 Python stops on the loop, line {line}")
ok(q["code"].split("\n")[q["line"] - 1].strip() == "gate = team.sort()", "B-4 keyed line is the one to change")
ok(shown(q["code"].replace("gate = team.sort()", "gate = sorted(team)")) == "Anu\nKiran\nRavi\n['Ravi', 'Anu', 'Kiran']", "B-4 fix works")
ok(shown(q["code"].replace("for name in gate:", "for name in team:")) != "Anu\nKiran\nRavi\n['Ravi', 'Anu', 'Kiran']", "B-4 changing only the loop line is not a fix")
ok(q["errors"][1].startswith("Nothing") and "Anu, Kiran, Ravi" in q["errors"][1], "B-4 'nothing' option describes the wanted output")
for q in Q.values():
    if q["type"] == "debug":
        ok(1 <= q["line"] <= len(q["code"].split("\n")) and 0 <= q["error"] < len(q["errors"]), f"{q['id']} line/error in range")
        ok(len(set(q["errors"])) == len(q["errors"]), f"{q['id']} duplicate errors")

# ---------- coding: reference passes every test; the starter fails one or breaks a rule ----------
for q in Q.values():
    if q["type"] != "coding":
        continue
    ch = q["challenge"]
    for k in ("title", "statement", "input_fmt", "output_fmt", "starter", "tests"):
        ok(bool(ch.get(k)), f"{q['id']} challenge needs {k}")
    ok(3 <= len(ch["tests"]) <= 5, f"{q['id']} has {len(ch['tests'])} tests")
    ok(any(not t.get("hidden") for t in ch["tests"]) and any(t.get("hidden") for t in ch["tests"]), f"{q['id']} sample + hidden")
    ok(all(t.get("note") for t in ch["tests"] if t.get("hidden")), f"{q['id']} every hidden test has a note")
    for t in ch["tests"]:
        out, et, em, _, _ = run(q["solution"], t["stdin"])
        ok(et is None and same_output(out, t["expected"]), f"{q['id']} solution on {t['stdin']!r}: {out!r} {et} {em}")
    ok(not check_rules(q, q["solution"]), f"{q['id']} solution breaks a rule: {check_rules(q, q['solution'])}")
    starter_pass = passes(ch["starter"], ch["tests"])
    ok(not starter_pass or check_rules(q, ch["starter"]), f"{q['id']} starter already passes")
    ok(not passes(ch["starter"], [t for t in ch["tests"] if not t.get("hidden")]), f"{q['id']} starter fails a sample test")
    ok(not check_rules(q, ch["starter"]) or bool(q.get("rules")), f"{q['id']} rules")
    pub = public_question(q)
    ok(all(("expected" in t) == (not t["hidden"]) for t in pub["challenge"]["tests"]), f"{q['id']} hidden expected outputs stay secret")

# the starters fail the way their statements say
r = run(Q["L5-1"]["challenge"]["starter"], "3\nRavi\nAnu\nKiran")
ok(r[1] == "AttributeError" and r[2] == "'NoneType' object has no attribute 'append'" and r[3] == 5, f"L5-1 starter crashes on the second name: {r[1]}: {r[2]} line {r[3]}")
ok(shown(Q["L5-1"]["challenge"]["starter"], "1\nSai") == "None", "L5-1 starter prints None for one name")
ok(check_rules(Q["L5-1"], Q["L5-1"]["challenge"]["starter"]) == ["append() gives back None: call it, don't store what it gives back."], "L5-1 rule catches team = team.append")
ok(check_rules(Q["L5-1"], 'n = int(input())\nteam = []\nfor i in range(n):\n    team += [input()]\nprint(team)\n') == ["Add each name with append()."], "L5-1 rule asks for append()")
ok(shown(Q["L5-3"]["challenge"]["starter"], "9") == "34", "L5-3 starter prints f(N) only (deck: 9 -> 34)")
ok(shown(Q["L5-3"]["challenge"]["starter"], "3") == "2", "L5-3 deck: 3 -> 2")
ok(Q["L5-3"]["challenge"]["tests"][0]["expected"].endswith("\n34") and Q["L5-3"]["challenge"]["tests"][1]["expected"].endswith("\n2"), "L5-3 samples are the deck's I/O")
# a beginner's iterative answer passes L5-3 too, and range(n) is the off-by-one the trap names
ITER = 'n = int(input())\nseries = [0, 1]\nfor i in range(2, n + 1):\n    series.append(series[i - 1] + series[i - 2])\nif n == 0:\n    series = [0]\nprint(series)\nprint(series[n])\n'
ok(passes(ITER, Q["L5-3"]["challenge"]["tests"]) and not check_rules(Q["L5-3"], ITER), "L5-3 iterative answer passes")
ok(not passes(Q["L5-3"]["solution"].replace("range(n + 1)", "range(n)"), Q["L5-3"]["challenge"]["tests"]), "L5-3 range(n) fails")
r = run(Q["B-2"]["challenge"]["starter"], "Ravi Anu Ravi Kiran Ravi")
ok(r[0].rstrip("\n").split("\n")[-1] == "['Anu', 'Kiran', 'Ravi', 'Ravi', 'Ravi']","B-2 starter's last line is the sorted sheet")
ok(r[0].rstrip("\n").split("\n")[:-1] == ["Anu 1", "Kiran 1", "Ravi 3"], "B-2 starter's counts are right: only the order is broken")
ok(set(check_rules(Q["B-2"], Q["B-2"]["challenge"]["starter"])) == {r_["msg"] for r_ in Q["B-2"]["rules"]}, "B-2 starter breaks every rule")
fixed_order_only = Q["B-2"]["challenge"]["starter"].replace("shifts.sort()\n", "").replace("for name in shifts:", "for name in sorted(shifts):")
ok(passes(fixed_order_only, Q["B-2"]["challenge"]["tests"]) and check_rules(Q["B-2"], fixed_order_only) == ["Count each name with count().", "Remove the counting loop: count() does that job."],"B-2 output fix alone still needs count()")

# ---------- deck examples, exactly as taught ----------
DECK = [
    ("list_a = []\nfor x in range(1,4):\n    list_a.append(x)\nprint(list_a)", "[1, 2, 3]"),
    ("list_a = [1, 2, 3]\nlist_b = [4, 5, 6]\nlist_a.extend(list_b)\nprint(list_a)", "[1, 2, 3, 4, 5, 6]"),
    ("list_a = [1, 2, 3]\nlist_a.insert(1,4)\nprint(list_a)", "[1, 4, 2, 3]"),
    ("list_a = [1, 2, 3]\nlist_a.pop()\nprint(list_a)", "[1, 2]"),
    ("list_a = [1, 3, 2, 3]\nlist_a.remove(3)\nprint(list_a)", "[1, 2, 3]"),
    ("list_a = [1, 2, 3]\nlist_a.clear()\nprint(list_a)", "[]"),
    ("list_a = [1, 3, 2, 3]\nindex =list_a.index(3)\nprint(index)", "1"),
    ("list_a = [1, 2, 3]\ncount = list_a.count(2)\nprint(count)", "1"),
    ("list_a = [1, 3, 2]\nlist_a.sort()\nprint(list_a)", "[1, 2, 3]"),
    ("list_a = [1, 3, 2]\nsorted(list_a)\nprint(list_a)", "[1, 3, 2]"),
    ("def multiply(n):\n   if n == 1:\n       return 1\n   return n * multiply(n - 1)\nnum = int(input())\nresult = multiply(num)\nprint(result)", None),
]
for code, want in DECK:
    if want is not None:
        ok(shown(code) == want, f"deck example {code.splitlines()[-1]!r} -> {shown(code)!r}")
ok(shown(DECK[-1][0], "4") == "24", "deck multiply(4)")
fib_deck = "def fib(n):\n    if n == 0:\n        return 0\n    if n == 1:\n        return 1\n    return fib(n - 1) + fib(n - 2)\nprint([fib(i) for i in range(7)])"
ok(shown(fib_deck) == "[0, 1, 1, 2, 3, 5, 8]", "deck: the series 0, 1, 1, 2, 3, 5, 8")
ok(run(C.UI["lab_starter"])[1] is None, "lab starter runs")
ok(shown(C.UI["lab_starter"]) == "['Ravi', 'Divya', 'Anu', 'Kiran', 'Sai']\nSai ['Ravi', 'Divya', 'Anu', 'Kiran']\n['Anu', 'Divya', 'Kiran', 'Ravi'] ['Ravi', 'Divya', 'Anu', 'Kiran']\n2 1", "lab starter output")

# ---------- untaught features never appear in what students read or run ----------
UNTAUGHT = [
    (r"\blambda\b", "lambda"), (r"\bkey\s*=", "key="), (r"\btry\s*:", "try"), (r"\bexcept\b", "except"),
    (r"\[[^\]\n]*\bfor\b[^\]\n]*\bin\b", "a comprehension"), (r"\{", "a dictionary or set"), (r"\.pop\(\s*[^)\s]", "pop(index)"),
    (r"\[[^\]\n]*:[^\]\n]*\]", "slicing"), (r"\.reverse\(", "reverse()"), (r"\.copy\(", "copy()"), (r"\bdel\b", "del"),
    (r"\.items\(|\.keys\(|\.values\(", "dictionary methods"), (r"\bimport\b", "import"),
]


def student_text(q):
    parts = [q.get("title", ""), q.get("code", ""), q.get("assertion", ""), q.get("reason", "")]
    for k in ("options", "items", "left", "right", "errors", "categories"):
        parts += [str(x) for x in q.get(k) or []]
    if q["type"] == "coding":
        ch = q["challenge"]
        parts += [ch["starter"], q["solution"], ch["statement"], ch["input_fmt"], ch["output_fmt"]] + [t["stdin"] for t in ch["tests"]]
    return "\n".join(parts)


for q in Q.values():
    text = student_text(q)
    for pat, what in UNTAUGHT:
        ok(not re.search(pat, text), f"{q['id']} uses untaught {what}")
for lvl in C.LEVELS:
    for pat, what in UNTAUGHT:
        ok(not re.search(pat, lvl["demo"]), f"{lvl['id']} demo uses untaught {what}")
for pat, what in UNTAUGHT:
    ok(not re.search(pat, C.UI["lab_starter"]), f"lab starter uses untaught {what}")
ok("₹" not in repr(C.Q) + repr(C.LEVELS) + repr(C.UI), "no rupee sign (the font lacks it)")
ok(not re.search(r"\bid\(", repr(C.Q)), "never asks for id() numbers")

# ---------- metadata ----------
LEVELS_OK = {"Recall", "Read", "Implement", "Debug", "Extend", "Optimize", "Prompting"}
for q in Q.values():
    ok(q["level"] in LEVELS_OK and q["concept"] in C.CONCEPTS and q["type"] in C.TYPE_LABEL, f"{q['id']} metadata")
    ok(bool(q.get("hints")) and bool(q.get("explain")), f"{q['id']} hints/explain")
    ok(q["stage"] in C.LEVEL_BY_ID and q["id"] in C.LEVEL_BY_ID[q["stage"]]["main"], f"{q['id']} is in its stage")
    ok(q["xp"] == C.XP[q["type"]], f"{q['id']} xp")
    if q["type"] not in ("tf", "order", "match", "fill"):
        ok(bool(q.get("trap")), f"{q['id']} has a trap")
ok({q["level"] for q in Q.values()} == LEVELS_OK, "every cognitive level used")
ok({q["concept"] for q in Q.values()} == set(C.CONCEPTS), f"unused concepts {set(C.CONCEPTS) - {q['concept'] for q in Q.values()}}")
ok({q["type"] for q in Q.values()} == set(C.TYPE_LABEL), f"unused types {set(C.TYPE_LABEL) - {q['type'] for q in Q.values()}}")
ok(not {"land", "board"} & set(C.TYPE_LABEL), "no S29/S30-only types")
ok(sum(q["type"] == "coding" for q in Q.values()) == 3, "three coding challenges")
ok([q["stage"] for q in Q.values() if q["type"] == "coding"] == ["L5", "L5", "BOSS"], "coding in L5 and BOSS")
ok(C.TOTAL == 28 == len(Q), "28 questions")
ok(sum(q["concept"] == "recap" for q in Q.values()) <= 3, "the recursion recap is at most 3 questions")
ok(Q["L0-1"]["type"] == "mcq" and Q["L0-2"]["type"] == "tf" and C.LEVEL_BY_ID["L0"]["main"][:2] == ["L0-1", "L0-2"], "L0 opens with the mcq and the tf")
ok(len(C.LEVEL_BY_ID["L0"]["main"]) + len(C.LEVEL_BY_ID["L1"]["main"]) >= 5, "L0 + L1 can earn the 5-combo")
ok(len(Q["L0-1"]["options"]) >= 3, "L0-1 has two wrong options to try")
ok(any(len(Q[x]["hints"]) >= 2 for l in C.LEVELS[1:] for x in l["main"]), "a later question has two hints")
ok(C.VISUAL_PRO[0] in C.TYPE_LABEL and C.VISUAL_PRO[1] in C.BADGES, "VISUAL_PRO names a used type and a badge")
ok(set(C.STAGE_BADGE.values()) <= set(C.BADGES) and set(C.STAGE_BADGE) == {l["id"] for l in C.LEVELS} - {"L0"}, "stage badges")
ok({"predict", "coding"} <= {k for k, _, _ in C.FEEDBACK_HELPED}, "feedback lists predict and coding")
UI_KEYS = {"id", "title", "short", "hero_h1", "hero_p", "story", "lab", "lab_name", "lab_starter", "boss_win", "champion", "guide_title", "guide_html"}
ok(UI_KEYS <= set(C.UI), f"UI keys missing {UI_KEYS - set(C.UI)}")
ok(C.UI["lab"] == "py" and C.UI["id"] == "lmethods", "py lab, mission id")
# Timers are sized per question (base + per line of code, with a floor); the 45-minute clock is the hard stop.
ok(C.MISSION_MINUTES == 45, "45-minute mission")
for q in Q.values():
    ok(q["time"] == C.timer(q) and q["time"] >= C.FLOOR.get(q["type"], 0), f"{q['id']} timer {q['time']} s")
ok(all(q["time"] == 360 for q in Q.values() if q["type"] == "coding"), "coding gets 6 minutes")
worst = sum(q["time"] for q in Q.values())
ok(45 * 60 <= worst <= 52 * 60, f"every timer used in full is {worst / 60:.1f} min: the clock, not the timers, ends a slow mission")

print(f"\n{N[0]} checks, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
