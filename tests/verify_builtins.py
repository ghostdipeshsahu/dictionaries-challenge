"""Run every Built-in Functions answer, option, worked example, fix and coding test in real Python.

    MISSION=builtins python tests/verify_builtins.py      (MISSION is set here if missing)
"""
import contextlib
import io
import itertools
import os
import re
import sys

os.environ.setdefault("MISSION", "builtins")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import mission_builtins as C  # noqa: E402
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
        except SyntaxError as e:  # raised by compile(): nothing ran
            err = ("SyntaxError", e.msg, e.lineno)
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


def replace_line(code, n, new):
    lines = code.split("\n")
    lines[n - 1] = new
    return "\n".join(lines)


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
    ok(bool(lvl.get("job")) and bool(lvl.get("intel_title")) and 1 <= len(lvl["intel"]) <= 3, f"{lvl['id']} needs a job, an intel title and intel")
ok(shown(C.UI["lab_starter"]) == "0 51 104\n[51, 34, 12, 7, 0]\nFalse True\n1 Teja\n2 Ravi\n3 Kiran", f"lab starter prints {shown(C.UI['lab_starter'])!r}")

# ---------- predict: the keyed option is Python's output, no distractor equals it ----------
for q in Q.values():
    if q["type"] == "predict":
        actual = shown(C.BOSS_SCENARIO if q.get("scenario") else q["code"])
        ok(q["options"][q["answer"]] == actual, f"{q['id']} keyed {q['options'][q['answer']]!r} != Python {actual!r}")
        ok(actual not in [o for i, o in enumerate(q["options"]) if i != q["answer"]], f"{q['id']} a distractor equals the output")
    if q["type"] in ("mcq", "predict", "ar", "msq"):
        ok(len(set(q["options"])) == len(q["options"]), f"{q['id']} duplicate options")
        for k in q.get("why") or {}:
            ok(0 <= k < len(q["options"]) and k != q.get("answer"), f"{q['id']} why key {k}")
    if q["type"] in ("mcq", "predict", "ar"):
        ok(set(q.get("why") or {}) == set(range(len(q["options"]))) - {q["answer"]}, f"{q['id']} every wrong option needs a why")

# ---------- numeric ----------
for q in Q.values():
    if q["type"] == "numeric":
        ok(shown(q["code"]) == str(q["value"]), f"{q['id']} numeric {shown(q['code'])!r} vs {q['value']}")
ok(shown(Q["L1-1"]["code"].replace("print(runs)", "print(runs + 4)")) == "56", "L1-1 the trap answer 56 is the inside value")
ok(shown(Q["L4-3"]["code"].replace("enumerate(names)", "enumerate(names, 1)")) == "3", "L4-3 the trap answer 3 is counting from 1")

# ---------- the L0 analogies, in Python ----------
q = Q["L0-1"]
ok(q["type"] == "mcq" and q["answer"] == 0, "L0-1 is an mcq keyed 0 (generic tests)")
ok(shown('def write(book):\n    book += [4]\nbook = [1, 0]\nwrite(book)\nprint(book)') == "[1, 0, 4]", "L0-1 a list passed in is changed")
q = Q["L0-2"]
ok(q["type"] == "tf" and q["value"] is True, "L0-2 is a tf keyed True (generic tests)")
ok(shown('def note(score):\n    score += 4\nscore = 52\nnote(score)\nprint(score)') == "52", "L0-2 a number passed in is not changed")
_, _, _, _, env = run('runs = 52\nbefore = id(runs)\nruns += 4')
ok(env["before"] != id(env["runs"]), "a number += makes a new object")
_, _, _, _, env = run('over = [1, 0]\nbefore = id(over)\nover += [4]\nafter_plus_eq = id(over)\nover = over + [4]')
ok(env["before"] == env["after_plus_eq"] and env["before"] != id(env["over"]), "list += keeps the object, + makes a new one")

# ---------- mcq on code: only the keyed over is a maiden ----------
q = Q["L4-2"]
maiden = [shown(f"print(any({o}))") == "False" for o in q["options"]]
ok([i for i, m in enumerate(maiden) if m] == [q["answer"]], f"L4-2 any() is False for {maiden}")

# ---------- ar ----------
q = Q["L3-3"]
ok(q["answer"] == 0 and q["options"] == C.AR_OPTIONS, "L3-3 ar keyed")
_, _, _, _, env = run(f'runs = {C.RUNS}\na = sorted(runs)\nb = sorted(runs, reverse=False)')
ok(env["a"] == env["b"] == [0, 7, 12, 34, 51], "L3-3 sorted(runs) == sorted(runs, reverse=False), low to high")

# ---------- fill: every accepted answer gives the expected output ----------
for q in Q.values():
    if q["type"] == "fill":
        parts = q["code"].split("___")
        ok(len(parts) - 1 == len(q["blanks"]), f"{q['id']} blank count")
        for combo in itertools.product(*q["blanks"]):
            code = parts[0] + "".join(b + p for b, p in zip(combo, parts[1:]))
            ok(shown(code) == q["expect"], f"{q['id']} with {combo} prints {shown(code)!r}")
        wrong = parts[0] + "".join(b + p for b, p in zip(["sorted", "key"], parts[1:]))
        ok(shown(wrong) != q["expect"], f"{q['id']} a wrong blank must not print the target")

# ---------- order: the keyed order is the only one that prints the target ----------
for q in Q.values():
    if q["type"] == "order":
        ok(shown("\n".join(q["items"][i] for i in q["mapping"])) == q["expect"], f"{q['id']} keyed order")
        wins = [pm for pm in itertools.permutations(range(len(q["items"]))) if shown("\n".join(q["items"][i] for i in pm)) == q["expect"]]
        ok(wins == [tuple(q["mapping"])], f"{q['id']} has {len(wins)} winning orders")

# ---------- categorize ----------
q = Q["L1-3"]
for item, k in zip(q["items"], q["mapping"]):
    got = shown(item + "\n" + q["setup"] + "\nf(over)\nprint(over)")
    ok(got == q["categories"][k], f"L1-3 {item} -> {got!r}, keyed {q['categories'][k]!r}")
q = Q["L3-5"]
for item, k in zip(q["items"], q["mapping"]):
    got = shown(q["setup"] + "\n" + item + "\nprint(runs)")
    ok(got == q["categories"][k], f"L3-5 {item} -> {got!r}, keyed {q['categories'][k]!r}")
for q in (Q["L1-3"], Q["L3-5"]):
    ok(set(q["mapping"]) == set(range(len(q["categories"]))), f"{q['id']} every group is used")

# ---------- match ----------
q = Q["L2-2"]
for i, expr in enumerate(q["left"]):
    got = shown(q["setup"] + f"\nprint({expr})")
    ok(got == q["right"][q["mapping"][i]], f"L2-2 {expr} -> {got!r}, keyed {q['right'][q['mapping'][i]]!r}")
ok(sorted(q["mapping"]) == list(range(len(q["right"]))) and q["code"] == q["setup"], "L2-2 mapping one-to-one, code shown = code checked")

# ---------- msq ----------
q = Q["B-2"]
ok(shown(q["code"]) == "[4, 16, 1, 9, 25]", f"B-2 the program as given prints {shown(q['code'])!r}")
for i, opt in enumerate(q["options"]):
    m = re.match(r"^Line (\d+): (.*)$", opt)
    ok(bool(m), f"B-2 option {i} names a line")
    n, new = int(m.group(1)), m.group(2)
    old = q["code"].split("\n")[n - 1]
    ok(old.split("(")[0].split(" ")[0] == new.split("(")[0].split(" ")[0], f"B-2 option {i} replaces a line of the same kind")
    got = shown(replace_line(q["code"], n, (old[:len(old) - len(old.lstrip())]) + new))
    ok((got == "[1, 4, 9, 16, 25]") == (i in q["answers"]), f"B-2 option {i} {opt!r} prints {got!r}")
q = Q["B-4"]
ok(q["answers"] == [0, 1, 2, 3], "B-4 spec answers")
ok(shown("print(max([34, 0, 12]))\nprint(max([0, 0, 0]))") == "34\n0", "B-4 the example and edge case hold for max()")

# ---------- debug missions ----------
q = Q["L1-5"]
_, et, em, line, _ = run(q["code"])
ok(et == "SyntaxError" and line == q["line"], f"L1-5 {et} on line {line}")
ok(q["errors"][q["error"]].startswith("SyntaxError") and "default" in em, f"L1-5 error {em!r}")
if sys.version_info[:2] < (3, 12):
    ok(q["errors"][q["error"]] == f"{et}: {em}", f"L1-5 the deck's wording matches Python {sys.version_info[:2]}: {em!r}")
ok(shown(q["code"].replace('def score_line(name="Meera", runs):', 'def score_line(runs, name="Meera"):')) == "Meera 52", "L1-5 fix works")
q = Q["L2-5"]
_, et, em, line, _ = run(q["code"])
ok(line == q["line"], f"L2-5 stops on line {line}, keyed {q['line']}")
ok(q["errors"][q["error"]] == f"{et}: {em}", f"L2-5 error {et}: {em!r}")
ok(shown(q["code"]).startswith("Top score: 51\n"), "L2-5 line 3 still prints before the crash")
ok(q["code"].split("\n")[q["focus"] - 1].startswith("max = "), "L2-5 focus is the line that hides max")
ok(shown(q["code"].replace("max = max(runs)", "top = max(runs)").replace('"Top score:", max)', '"Top score:", top)')) == "Top score: 51\nTop score: 60", "L2-5 fix works")
q = Q["B-5"]
out, et, _, _, env = run(q["code"])
ok(et is None and out.strip() == "[4, 6]" and q["errors"][q["error"]].startswith("It prints [4, 6]"), f"B-5 prints {out!r}")
ok(env["first"] is env["second"], "B-5 both calls return the one default list")
ok(q["code"].split("\n")[q["line"] - 1].startswith("def new_over(ball, over=[])"), "B-5 keyed line is the default list")
fixed = q["code"].replace("def new_over(ball, over=[]):\n    over += [ball]", "def new_over(ball):\n    over = [ball]")
ok(shown(fixed + "\nprint(first)") == "[6]\n[4]", "B-5 fix works")
_, et, em, _, _ = run(q["code"].replace("over=[]", "over"))
ok(f"{et}: {em}" == q["errors"][2], f"B-5 distractor TypeError is real Python wording: {et}: {em}")

# ---------- coding: reference passes every test; the starter fails one or breaks a rule ----------
for q in Q.values():
    if q["type"] != "coding":
        continue
    ch = q["challenge"]
    ok(3 <= len(ch["tests"]) <= 5, f"{q['id']} 3 to 5 tests")
    ok(any(not t.get("hidden") for t in ch["tests"]) and any(t.get("hidden") for t in ch["tests"]), f"{q['id']} sample + hidden")
    ok(all(t.get("note") for t in ch["tests"] if t.get("hidden")), f"{q['id']} every hidden test has a note")
    for t in ch["tests"]:
        out, et, em, _, _ = run(q["solution"], t["stdin"])
        ok(et is None and same_output(out, t["expected"]), f"{q['id']} solution on {t['stdin']!r}: {out!r} {et} {em}")
    ok(not check_rules(q, q["solution"]), f"{q['id']} solution breaks a rule: {check_rules(q, q['solution'])}")
    starter_pass = all((lambda r: r[1] is None and same_output(r[0], t["expected"]))(run(ch["starter"], t["stdin"])) for t in ch["tests"])
    ok(not starter_pass or check_rules(q, ch["starter"]), f"{q['id']} starter already passes")
    ok(len(q["hints"]) >= 2 and q.get("explain") and q.get("trap"), f"{q['id']} hints, explain and trap")
    for k in ("title", "statement", "input_fmt", "output_fmt", "starter", "tests"):
        ok(bool(ch.get(k)), f"{q['id']} challenge needs {k}")
# the starters fail the way their statements say
ok(shown(Q["L5-2"]["challenge"]["starter"], "Teja Ravi\n34 0") == "Teja\nRavi", "L5-2 starter prints only the names")
ok(check_rules(Q["L5-2"], Q["L5-2"]["challenge"]["starter"]), "L5-2 starter has no enumerate")
ok(check_rules(Q["L5-2"], 'names = input().split()\nruns = input().split()\nfor i in range(len(names)):\n    print(i + 1, names[i], runs[i])\n'),
   "L5-2 a range() loop gives the right output but is refused")
q = Q["B-3"]
st = q["challenge"]["starter"]
ok(all(same_output(run(st, t["stdin"])[0], t["expected"]) for t in q["challenge"]["tests"] if not t.get("hidden")), "B-3 starter passes the samples")
ok(not all(same_output(run(st, t["stdin"])[0], t["expected"]) for t in q["challenge"]["tests"] if t.get("hidden")), "B-3 starter fails a hidden test")
ok(len(check_rules(q, st)) >= 3, f"B-3 starter breaks the rules: {check_rules(q, st)}")
strings = 'over = input().split()\nprint("Runs:", sum([0]))\nprint("Every ball scored:", all(over))\nprint("Maiden:", not any(over))\n'
ok(shown(strings, "0 4 4 4 4 4").split("\n")[1] == "Every ball scored: True", "B-3 trap: all() on strings counts '0' as true")

# ---------- deck numbers ----------
ok(shown('def increment(a):\n    a += 1\n\na = 5\nincrement(a)\nprint(a)') == "5", "deck: increment leaves a alone")
ok(shown('def add_item(list_x):\n    list_x += [3]\n\nlist_a = [1,2]\nadd_item(list_a)\nprint(list_a)') == "[1, 2, 3]", "deck: += changes the caller's list")
ok(shown('def add_item(list_x):\n    list_x = list_x + [3]\n\nlist_a = [1,2]\nadd_item(list_a)\nprint(list_a)') == "[1, 2]", "deck: = + does not")
ok(shown('def add_item(list_x=[]):\n    list_x += [3]\n    print(list_x)\n\nadd_item()\nadd_item([1,2])\nadd_item()') == "[3]\n[1, 2, 3]\n[3, 3]", "deck: the default list trap")
ok(run('def greet(arg_1="Hi", arg_2):\n    print(arg_1 + " " + arg_2)')[1] == "SyntaxError", "deck: non-default after default")
ok(shown('def greet(arg_1="Hi", arg_2="Ram"):\n    print(arg_1 + " " + arg_2)\ngreet()\ngreet("Hello")\ngreet("Hello","Teja")\ngreet(arg_2="Teja")') == "Hi Ram\nHello Ram\nHello Teja\nHi Teja", "deck: default arguments")
ok(shown('print(min(3,5,4))\nprint(min([1,-2,4,2]))') == "3\n-2", "deck: min")
ok(shown('print(min("Python", "Java"))') == "Java" and ord("P") == 80 and ord("J") == 74, "deck: min of strings")
ok(shown('print(max(3,5,4))\nprint(max([1,-2,4,2]))') == "5\n4", "deck: max")
ok(shown('print(sum([1,-2,4,2]))') == "5", "deck: sum")
ok(shown('list_a = [3, 5, 2, 1, 4, 6]\nlist_x = sorted(list_a)\nprint(list_x)\nprint(list_a)') == "[1, 2, 3, 4, 5, 6]\n[3, 5, 2, 1, 4, 6]", "deck: sorted returns a new list")
ok(shown('list_a = [3, 5, 2, 1, 4, 6]\nprint(sorted(list_a, reverse=True))') == "[6, 5, 4, 3, 2, 1]", "deck: sorted reverse")
ok(shown('list_a = [2, 4, 1, 3, 5]\nlist_x = []\nfor item in list_a:\n    list_x += [item*item]\nprint(list_x)') == "[4, 16, 1, 9, 25]", "deck: the daily challenge's mistake")
# teacher's takeaways beyond the deck
_, _, _, _, env = run('list_a = [1, 2]\nlist_b = list(list_a)\nlist_c = list_a\nlist_a += [3]')
ok(env["list_b"] == [1, 2] and env["list_c"] == [1, 2, 3] and env["list_b"] is not env["list_a"], "list() copies, = only names")
ok(shown('a = [1, 2, 3]\nprint(a.reverse())\nprint(a)') == "None\n[3, 2, 1]", "reverse() is in place and returns None")
ok(shown('print(all([]), any([]), all([1, 2]), any([0, 0]))') == "True False True False", "all/any basics")
ok(shown('print(list(reversed("Teja")))') == "['a', 'j', 'e', 'T']", "reversed works on a string")
ok(shown('print(list(enumerate(["Teja", "Ravi"])))') == "[(0, 'Teja'), (1, 'Ravi')]", "enumerate pairs")
ok(shown('print(min("apple", "Banana"))') == "Banana", "capitals come first")

# ---------- the scenario: three names, two lists ----------
_, _, _, _, env = run(C.BOSS_SCENARIO)
ok(env["score"] == 98 and env["last_over"] == [4, 1, 6, 0, 2, 0] and env["card"] == [4, 1, 6, 0, 2], "scenario state")
ok(env["card"] is not env["last_over"], "scenario: card is a separate list")

# ---------- untaught features never appear (explanations may name them) ----------
UNTAUGHT = [r"\.append\(", r"\.extend\(", r"\.insert\(", r"\.pop\(", r"\.remove\(", r"\.sort\(", r"\.copy\(",
            r"\.index\(", r"\.count\(", r"\.clear\(", r"\blambda\b", r"\bkey\s*=", r"\btry\b", r"\bexcept\b",
            r"\bdict\b", r"isdigit", r"\[[^\]\n]*\bfor\b[^\]\n]*\]", r"::-1", r"\bimport\b", r"\.items\(", r"\.get\("]
for q in Q.values():
    blob = repr({k: v for k, v in q.items() if k not in ("why", "trap", "explain", "rules")})
    for pat in UNTAUGHT:
        ok(not re.search(pat, blob), f"{q['id']} uses untaught {pat}")
    codes = [q.get("code") or "", q.get("solution") or "", q.get("setup") or "", (q.get("challenge") or {}).get("starter", "")]
    ok(not any("{" in c or "}" in c for c in codes), f"{q['id']} code uses braces (dictionaries are not taught)")
for name, code in [(l["id"] + " demo", l["demo"]) for l in C.LEVELS] + [("lab starter", C.UI["lab_starter"]), ("scenario", C.BOSS_SCENARIO)]:
    ok(not any(re.search(p, code) for p in UNTAUGHT) and "{" not in code, f"{name} uses something untaught")
# a recursive def would call itself
for q in Q.values():
    for code in (q.get("code") or "", q.get("solution") or ""):
        for fn in re.findall(r"def (\w+)\(", code):
            body = code.split(f"def {fn}(", 1)[1]
            ok(f"{fn}(" not in body.split("\n\n")[0].split("\n", 1)[-1], f"{q['id']} {fn} is recursive")
ok("₹" not in repr(C.QUESTIONS) + repr(C.UI) + repr(C.LEVELS), "no rupee sign (the font lacks it)")

# ---------- metadata ----------
LEVELS_OK = {"Recall", "Read", "Implement", "Debug", "Extend", "Optimize", "Prompting"}
for q in Q.values():
    ok(q["level"] in LEVELS_OK and q["concept"] in C.CONCEPTS and q["type"] in C.TYPE_LABEL, f"{q['id']} metadata")
    ok(bool(q.get("hints")) and bool(q.get("explain")), f"{q['id']} hints/explain")
    ok(q["xp"] == C.XP[q["type"]], f"{q['id']} xp")
    if q["type"] in ("match", "categorize", "order"):
        n = len(q["left"]) if q["type"] == "match" else len(q["items"])
        ok(len(q["mapping"]) == n, f"{q['id']} mapping length")
    if q["type"] == "debug":
        ok(1 <= q["line"] <= len(q["code"].split("\n")) and 0 <= q["error"] < len(q["errors"]) and len(set(q["errors"])) == len(q["errors"]), f"{q['id']} debug key")
    if q["type"] == "msq":
        ok(1 <= len(q["answers"]) < len(q["options"]) and q["answers"] == sorted(set(q["answers"])), f"{q['id']} msq answers")
ok({q["level"] for q in Q.values()} == LEVELS_OK, "every cognitive level used")
ok({q["concept"] for q in Q.values()} == set(C.CONCEPTS), f"unused concepts {set(C.CONCEPTS) - {q['concept'] for q in Q.values()}}")
ok({q["type"] for q in Q.values()} == set(C.TYPE_LABEL), f"unused types {set(C.TYPE_LABEL) - {q['type'] for q in Q.values()}}")
ok(not {"land", "board"} & set(C.TYPE_LABEL), "no land or board questions")
ok(sum(q["type"] == "coding" for q in Q.values()) == 2, "two coding challenges")
ok({q["stage"] for q in Q.values() if q["type"] == "coding"} == {"L5", "BOSS"}, "coding sits in L5 and the Boss")
ok(C.TOTAL == 25 == len(Q), f"25 questions, got {C.TOTAL}")
ok([l["id"] for l in C.LEVELS] == ["L0", "L1", "L2", "L3", "L4", "L5", "BOSS"] and not any(l.get("bonus") for l in C.LEVELS), "7 stages, no bonus round")
ok(C.LEVELS[0]["main"][:2] == ["L0-1", "L0-2"] and C.LEVELS[1]["main"][0] == "L1-1", "first questions where the generic tests expect them")
ok(sum(len(C.LEVEL_BY_ID[x]["main"]) for x in ("L0", "L1")) >= 5, "L0 + L1 give a 5-answer combo")
ok(any(len(Q[x]["hints"]) >= 2 for l in C.LEVELS[1:] for x in l["main"]), "a later question has two hints")
ok(set(C.STAGE_BADGE) == {"L1", "L2", "L3", "L4", "L5", "BOSS"} and set(C.STAGE_BADGE.values()) <= set(C.BADGES), "stage badges")
ok(C.VISUAL_PRO[0] in C.TYPE_LABEL and C.VISUAL_PRO[1] in C.BADGES, "VISUAL_PRO badge")
ok(set(C.BADGES) == set(C.STAGE_BADGE.values()) | {"combo-5", "clean-sweep", C.VISUAL_PRO[1]}, "every badge can be earned")
UI_KEYS = {"id", "title", "short", "hero_h1", "hero_p", "story", "lab", "lab_name", "lab_starter", "boss_win", "champion", "guide_title", "guide_html"}
ok(UI_KEYS <= set(C.UI) and C.UI["id"] == "builtins" and C.UI["lab"] == "py", f"UI keys {UI_KEYS - set(C.UI)}")
ok("Your 3 jobs" in C.UI["story"], "story has 3 jobs")
ok({k for k, _, _ in C.FEEDBACK_HELPED} >= {"predict", "coding", "lab", "hints"} and C.FEEDBACK_TOPIC, "feedback options")
ok(all(k in C.TYPE_LABEL or k in ("lab", "hints", "xp") for k, _, _ in C.FEEDBACK_HELPED), "feedback options are this mission's")
# Timers are sized per question (base + per line of code, with a floor); the 45-minute clock is the hard stop.
ok(C.MISSION_MINUTES == 45, "45-minute mission")
for q in Q.values():
    ok(q["time"] == C.timer(q) and q["time"] >= C.FLOOR.get(q["type"], 0), f"{q['id']} timer {q['time']} s")
ok(all(q["time"] == 360 for q in Q.values() if q["type"] == "coding"), "coding gets 6 minutes")
worst = sum(q["time"] for q in Q.values())
ok(worst <= 38 * 60, f"every timer used in full is {worst / 60:.1f} min: it fits the 45-minute clock, with time to read each stage")

print(f"\n{N[0]} checks, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
