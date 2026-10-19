"""Run every Working with Lists answer, option, worked example, deck example and coding test in real Python.

    MISSION=wlists python tests/verify_wlists.py      (MISSION is set here if missing)
"""
import contextlib
import io
import itertools
import os
import re
import sys

os.environ.setdefault("MISSION", "wlists")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import mission_s30 as S30  # noqa: E402
from app import mission_wlists as C  # noqa: E402
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


def passes(code, t):
    out, et, _, _, _ = run(code, t["stdin"])
    return et is None and same_output(out, t["expected"])


Q = C.QUESTIONS

# ---------- demos and worked examples: what the steps show is exactly what Python prints ----------
for lvl in C.LEVELS:
    out, et, em, _, _ = run(lvl["demo"])
    ok(et is None, f"{lvl['id']} demo raised {et}: {em}")
    shows = [w["shows"] for w in lvl["walk"] if "shows" in w]
    ok("\n".join(shows) == out.rstrip("\n"), f"{lvl['id']} walk shows {shows!r} but Python prints {out!r}")
    nlines = len(lvl["demo"].split("\n"))
    ok(all(1 <= w["line"] <= nlines and lvl["demo"].split("\n")[w["line"] - 1].strip() for w in lvl["walk"]), f"{lvl['id']} walk points at a blank or missing line")
    ok(bool(lvl.get("learn")) and bool(lvl.get("job")) and bool(lvl.get("intel_title")) and len(lvl["intel"]) >= 3, f"{lvl['id']} needs learn, job, intel_title and intel")
    for k in ("name", "difficulty"):
        ok(bool(lvl.get(k)), f"{lvl['id']} needs {k}")
ok([l["id"] for l in C.LEVELS] == ["L0", "L1", "L2", "L3", "L4", "L5", "BOSS"], "seven stages, L0 to BOSS")
ok(C.LEVEL_BY_ID["BOSS"]["demo"] == C.BOSS_SCENARIO, "the boss demo is the scenario")
ok(not any(l.get("bonus") for l in C.LEVELS), "no bonus round")

# ---------- predict: the keyed option is Python's output, no distractor equals it ----------
for q in Q.values():
    if q["type"] == "predict":
        code = C.BOSS_SCENARIO if q.get("scenario") else q["code"]
        actual = shown(code)
        ok(q["options"][q["answer"]] == actual, f"{q['id']} keyed {q['options'][q['answer']]!r} != Python {actual!r}")
        ok(actual not in [o for i, o in enumerate(q["options"]) if i != q["answer"]], f"{q['id']} a distractor equals the output")
        ok(len(set(q["options"])) == len(q["options"]), f"{q['id']} duplicate options")
        ok(all(shown(code) == actual for _ in range(3)), f"{q['id']} output is not the same on every run")
    if q["type"] in ("mcq", "predict", "ar", "msq"):
        for k in q.get("why") or {}:
            ok(0 <= k < len(q["options"]) and k != q.get("answer"), f"{q['id']} why key {k}")
    if q["type"] in ("mcq", "predict", "ar"):
        ok(set(q.get("why") or {}) == set(range(len(q["options"]))) - {q["answer"]}, f"{q['id']} every wrong option needs a why")

# ---------- numeric ----------
ok(shown(Q["L2-2"]["code"]) == str(Q["L2-2"]["value"]), f"L2-2 numeric {shown(Q['L2-2']['code'])!r}")
ok(shown(C.BOSS_SCENARIO + "\nprint(len(rahul) + len(anu))").split("\n")[-1] == str(Q["B-2"]["value"]), "B-2 numeric")
ok(shown('votes = [5, 3, 8]\nv = [5, 3, 8]\nv[1] = v[1] + 4\nvotes[0] = 6\nprint(votes[1] + v[0])') == "8", "L2-2 trap: with two lists it would differ")

# ---------- the scenario: who shares which list ----------
_, _, _, _, env = run(C.BOSS_SCENARIO)
ok(id(env["playlist"]) == id(env["rahul"]) == id(env["dj"][1]), "scenario: playlist, rahul and dj[1] are one list")
ok(id(env["anu"]) != id(env["playlist"]) and id(env["dj"]) != id(env["playlist"]), "scenario: anu and dj are separate lists")
ok(env["anu"] == ["Naatu Naatu", "Jai Ho", "Kesariya"], "scenario: anu keeps its 3 songs")

# ---------- recall questions, checked against Python ----------
_, _, _, _, env = run(f'playlist = {C.SONGS}\nrahul = playlist\nrahul[2] = "Butta Bomma"')
ok(C.QUESTIONS["L0-1"]["options"][C.QUESTIONS["L0-1"]["answer"]] == env["playlist"][2], "L0-1 shared list shows Rahul's swap")
_, _, _, _, env = run(f'playlist = {C.SONGS}\nanu = {C.SONGS}\nanu[0] = "Malhari"')
ok((env["playlist"][0] == "Naatu Naatu") == Q["L0-2"]["value"] and id(env["playlist"]) != id(env["anu"]), "L0-2 tf (a second list with the same songs)")
for obj in (5, 1.25, "A", [1, 2, 3]):
    ok(isinstance(id(obj), int), f"L1-2 id() works on {obj!r}")
ok(id([1, 2, 3]) not in (0, 1, 2), "L1-2 an id is not an index")
out = shown('a = "Hello"\nprint(id(a))\na = a + " World"\nprint(id(a))\nprint(a)').split("\n")
ok(out[0] != out[1] and out[2] == "Hello World" and Q["L1-4"]["answer"] == 0, "L1-4 ar: a + \" World\" gives a new id")

# ---------- msq ----------
q = Q["L1-3"]
truth = [shown(q["code"] + "\n" + o) == "True" for o in q["options"]]
ok([i for i, t in enumerate(truth) if t] == q["answers"], f"L1-3 truth {truth}")
ok(all(shown(q["code"] + "\n" + o) in ("True", "False") for o in q["options"]), "L1-3 every option prints True or False")

# ---------- mcq L3-5: only += makes both names show Malhari ----------
q = Q["L3-5"]
setup = 'playlist = ["Naatu Naatu", "Jai Ho"]\nrahul = playlist'
both = []
for o in q["options"]:
    _, et, _, _, env = run(setup + "\n" + o)
    both.append(et is None and "Malhari" in env["playlist"] and "Malhari" in env["rahul"])
ok([i for i, b in enumerate(both) if b] == [q["answer"]], f"L3-5 only the key reaches both names: {both}")

# ---------- fill: every accepted answer gives the expected output, the trap does not ----------
for q in Q.values():
    if q["type"] == "fill":
        parts = q["code"].split("___")
        ok(len(parts) - 1 == len(q["blanks"]), f"{q['id']} blank count")
        for combo in itertools.product(*q["blanks"]):
            code = parts[0] + "".join(b + p for b, p in zip(combo, parts[1:]))
            ok(shown(code) == q["expect"], f"{q['id']} with {combo} prints {shown(code)!r}")
ok(shown(Q["L4-4"]["code"].replace("___", "anu")) != Q["L4-4"]["expect"], "L4-4 dj += anu is not the answer")
ok(shown(Q["L4-4"]["code"].replace("___", "anu")).endswith("\n4"), "L4-4 dj += anu gives 4 loose songs")
ok(shown(Q["L2-3"]["code"].replace("___", "playlist", 1).replace("___", "0")) != Q["L2-3"]["expect"], "L2-3 index 0 is wrong")
_, _, _, _, env = run(Q["L2-3"]["code"].replace("___", "playlist", 1).replace("___", "1"))
ok(id(env["rahul"]) == id(env["playlist"]), "L2-3 rahul shares the playlist")

# ---------- order: the keyed order is the only one that prints the target ----------
q = Q["L2-5"]
ok(shown("\n".join(q["items"][i] for i in q["mapping"])) == q["expect"], "L2-5 keyed order")
wins = [pm for pm in itertools.permutations(range(len(q["items"]))) if shown("\n".join(q["items"][i] for i in pm)) == q["expect"]]
ok(wins == [tuple(q["mapping"])], f"L2-5 has {len(wins)} winning orders")
ok(sorted(q["mapping"]) == list(range(len(q["items"]))), "L2-5 mapping uses every line once")

# ---------- categorize ----------
q = Q["L3-3"]
for item, k in zip(q["items"], q["mapping"]):
    got = shown(q["setup"] + "\n" + item + "\nprint(list_b)")
    ok(got == q["categories"][k], f"L3-3 {item} -> {got!r}, keyed {q['categories'][k]!r}")
ok(set(q["mapping"]) == set(range(len(q["categories"]))), "L3-3 every group used")
q = Q["L4-5"]
base = shown(q["setup"] + "\nprint(box)")
ok(base == "[3, [1, 2]]" and q["categories"][1].endswith(base), f"L4-5 box starts as {base!r}")
for item, k in zip(q["items"], q["mapping"]):
    got = shown(q["setup"] + "\n" + item + "\nprint(box)")
    ok((got != base) == (k == 0), f"L4-5 {item} -> {got!r}, keyed {q['categories'][k]!r}")
ok(set(q["mapping"]) == {0, 1}, "L4-5 both groups used")

# ---------- match ----------
q = Q["L3-4"]
for i, expr in enumerate(q["left"]):
    got = shown(q["setup"] + f"\nprint({expr})")
    ok(got == q["right"][q["mapping"][i]], f"L3-4 {expr} -> {got!r}, keyed {q['right'][q['mapping'][i]]!r}")
ok(sorted(q["mapping"]) == list(range(len(q["right"]))) and q["code"] == q["setup"], "L3-4 mapping one-to-one, code shown = code checked")

# ---------- debug missions ----------
q = Q["L2-4"]
_, et, em, line, _ = run(q["code"])
ok(line == q["line"], f"L2-4 stops on line {line}, keyed {q['line']}")
ok(q["errors"][q["error"]] == f"{et}: {em}", f"L2-4 error {et}: {em!r} vs {q['errors'][q['error']]!r}")
ok(shown(q["code"].replace('rahul[3] = "Malhari"', 'rahul += ["Malhari"]')) == "['Naatu Naatu', 'Jai Ho', 'Kesariya', 'Malhari']", "L2-4 the fix in the explanation works")
for qid, bad, fix, want in (("L4-3", "animals += wild_animals", "animals += [wild_animals]", "['cat', 'dog', ['Tiger', 'Fox']]"),
                            ("B-5", "playlist = playlist + anu", "playlist += anu", "['Naatu Naatu', 'Jai Ho', 'Malhari', 'Kesariya']")):
    q = Q[qid]
    _, et, _, _, _ = run(q["code"])
    ok(et is None, f"{qid} runs without an error")
    ok(q["errors"][q["error"]] == "It prints " + shown(q["code"]), f"{qid} keyed {q['errors'][q['error']]!r} vs prints {shown(q['code'])!r}")
    ok(all(e != "It prints " + shown(q["code"]) for i, e in enumerate(q["errors"]) if i != q["error"]), f"{qid} a distractor is the real output")
    ok(q["code"].split("\n")[q["line"] - 1].strip() == bad, f"{qid} keyed line is the one to change")
    ok(shown(q["code"].replace(bad, fix)) == want, f"{qid} fix works: {shown(q['code'].replace(bad, fix))!r}")
    ok(q["focus"] == q["line"], f"{qid} focus on the keyed line")
ok(Q["L4-3"]["title"].count("['cat', 'dog', ['Tiger', 'Fox']]") == 1, "L4-3 states the Daily Challenge's expected output")
for q in Q.values():
    if q["type"] == "debug":
        ok(1 <= q["line"] <= len(q["code"].split("\n")) and 0 <= q["error"] < len(q["errors"]), f"{q['id']} line and error in range")
        ok(len(set(q["errors"])) == len(q["errors"]), f"{q['id']} duplicate errors")

# ---------- coding: reference passes every test; the starter fails one or breaks a rule ----------
for q in Q.values():
    if q["type"] != "coding":
        continue
    ch = q["challenge"]
    ok(3 <= len(ch["tests"]) <= 5, f"{q['id']} has 3 to 5 tests")
    ok(any(not t.get("hidden") for t in ch["tests"]) and any(t.get("hidden") for t in ch["tests"]), f"{q['id']} sample + hidden")
    ok(all(t.get("note") for t in ch["tests"] if t.get("hidden")), f"{q['id']} every hidden test has a note")
    for k in ("title", "statement", "input_fmt", "output_fmt", "starter"):
        ok(bool(ch.get(k)), f"{q['id']} challenge needs {k}")
    for t in ch["tests"]:
        out, et, em, _, _ = run(q["solution"], t["stdin"])
        ok(et is None and same_output(out, t["expected"]), f"{q['id']} solution on {t['stdin']!r}: {out!r} {et} {em}")
        _, et, em, _, _ = run(ch["starter"], t["stdin"])
        ok(et is None, f"{q['id']} starter runs on {t['stdin']!r} without crashing ({et}: {em})")
    ok(not check_rules(q, q["solution"]), f"{q['id']} solution breaks a rule: {check_rules(q, q['solution'])}")
    starter_pass = all(passes(ch["starter"], t) for t in ch["tests"])
    ok(not starter_pass, f"{q['id']} starter already passes the tests")
    ok(any(not passes(ch["starter"], t) for t in ch["tests"] if not t.get("hidden")), f"{q['id']} starter fails a sample test (the bug is visible)")
    ok(q["solution"] != ch["starter"], f"{q['id']} solution differs from the starter")
    ok(q["time"] == 360, f"{q['id']} gets 6 minutes")

# L5-1: the starter's backup follows the new song; the other fix (playlist = playlist + [...]) also passes
q = Q["L5-1"]
ok(shown(q["challenge"]["starter"], "1\nJai Ho\nKesariya").split("\n")[0] == "['Jai Ho', 'Kesariya']", "L5-1 starter shows the = trap")
alt = q["challenge"]["starter"].replace("playlist += [input()]\nprint", "playlist = playlist + [input()]\nprint")
ok(alt != q["challenge"]["starter"] and all(passes(alt, t) for t in q["challenge"]["tests"]), "L5-1 the second fix in the explanation passes")
# L5-2: two bugs; fixing only one still fails a sample
q = Q["L5-2"]
st = q["challenge"]["starter"]
ok(shown(st, q["challenge"]["tests"][0]["stdin"]) == "['Naatu Naatu', 'Jai Ho', 'Naatu Naatu', 'Jai Ho', 'Kesariya']\n5", "L5-2 starter gives one long, repeated list")
only_brackets = st.replace("set_list += block", "set_list += [block]")
ok(shown(only_brackets, q["challenge"]["tests"][0]["stdin"]) == "[['Naatu Naatu', 'Jai Ho', 'Kesariya'], ['Naatu Naatu', 'Jai Ho', 'Kesariya']]\n2", "L5-2 fixing only += leaves one shared block")
ok(not all(passes(only_brackets, t) for t in q["challenge"]["tests"] if not t.get("hidden")), "L5-2 fixing only += fails a sample")
only_inside = q["solution"].replace("set_list += [block]", "set_list += block")
ok(not all(passes(only_inside, t) for t in q["challenge"]["tests"] if not t.get("hidden")), "L5-2 fixing only block = [] fails a sample")
alt = q["solution"].replace("set_list += [block]", "set_list = set_list + [block]")
ok(all(passes(alt, t) for t in q["challenge"]["tests"]), "L5-2 set_list = set_list + [block] also works")
# B-3: the starter leaves rahul behind; moving rahul = playlist after the loop passes the tests but breaks a rule
q = Q["B-3"]
st = q["challenge"]["starter"]
ok(shown(st, "2\nJai Ho\nKesariya") == "['Naatu Naatu']\nFalse", "B-3 starter leaves rahul behind")
ok(check_rules(q, st), "B-3 starter breaks a rule")
cheat = st.replace("print(rahul)", "rahul = playlist\nprint(rahul)")
ok(all(passes(cheat, t) for t in q["challenge"]["tests"]) and check_rules(q, cheat), "B-3 the trap passes the tests but breaks a rule")
alt = q["solution"].replace("playlist += [song]", "rahul += [song]")
ok(all(passes(alt, t) for t in q["challenge"]["tests"]) and not check_rules(q, alt), "B-3 rahul += [song] is also accepted")
ok(sum(q["type"] == "coding" for q in Q.values()) == 3, "three coding challenges")
ok({q["stage"] for q in Q.values() if q["type"] == "coding"} == {"L5", "BOSS"}, "coding sits in L5 and the Boss")

# ---------- prompting msq: the spec's example is true for a real backup, and the wrong line is the bug ----------
ok(shown("playlist = ['Jai Ho']\nbackup = playlist + []\nplaylist += ['Malhari']\nprint(backup)") == "['Jai Ho']", "B-4 example holds for playlist + []")
ok(shown("playlist = ['Jai Ho']\nbackup = playlist\nplaylist += ['Malhari']\nprint(backup)") == "['Jai Ho', 'Malhari']", "B-4 backup = playlist fails the example")
ok(shown("playlist = []\nbackup = playlist + []\nprint(backup)") == "[]", "B-4 empty case")
ok(5 not in Q["B-4"]["answers"] and 4 not in Q["B-4"]["answers"], "B-4 wishes and the bug are not in the spec")

# ---------- the deck's examples, exactly as taught ----------
deck = [
    ('a = 2\nlist_a = [5, "Six", a, 8.2]\nprint(type(list_a))\nprint(list_a)', "<class 'list'>\n[5, 'Six', 2, 8.2]"),
    ('list_a = []\nprint(list_a)\nfor i in range(1,4):\n    list_a += [i]\nprint(list_a)', "[]\n[1, 2, 3]"),
    ('list_a = list(range(4))\nprint(list_a)', "[0, 1, 2, 3]"),
    ('list_a = [1, 2, 3, 5]\nprint(list_a)\nlist_a[3] = 4\nprint(list_a)', "[1, 2, 3, 5]\n[1, 2, 3, 4]"),
    ("animals = ['cat', 'dog']\nwild_animals = ['Tiger', 'Fox']\nanimals += wild_animals\nprint(animals)", "['cat', 'dog', 'Tiger', 'Fox']"),
    ("animals = ['cat', 'dog']\nwild_animals = ['Tiger', 'Fox']\nanimals += [wild_animals]\nprint(animals)", "['cat', 'dog', ['Tiger', 'Fox']]"),
    ('list_a = [1, 2, 3, 5]\nlist_b = list_a\nlist_b[3] = 4\nprint("list a : " + str(list_a))\nprint("list b : " + str(list_b))', "list a : [1, 2, 3, 4]\nlist b : [1, 2, 3, 4]"),
    ('list_a = [1, 2]\nlist_b = list_a\nlist_a = [6, 7]\nprint("list a : " + str(list_a))\nprint("list b : " + str(list_b))', "list a : [6, 7]\nlist b : [1, 2]"),
    ('list_a = [1, 2]\nlist_b = list_a\nlist_a = list_a + [6, 7]\nprint("list a : " + str(list_a))\nprint("list b : " + str(list_b))', "list a : [1, 2, 6, 7]\nlist b : [1, 2]"),
    ('list_a = [1, 2]\nlist_b = list_a\nlist_a += [6, 7]\nprint("list a : " + str(list_a))\nprint("list b : " + str(list_b))', "list a : [1, 2, 6, 7]\nlist b : [1, 2, 6, 7]"),
    ('list_a = [1,2]\nlist_b = [3, list_a]\nlist_a[1] = 4\nprint(list_a)\nprint(list_b)', "[1, 4]\n[3, [1, 4]]"),
    ('a = 2\nlist_a = [1,a]\nprint(list_a)\na = 3\nprint(list_a)', "[1, 2]\n[1, 2]"),
]
for i, (code, want) in enumerate(deck):
    ok(shown(code) == want, f"deck example {i + 1}: {shown(code)!r}")
ok(shown('list_a = [1, 2, 3]\nlist_b = [1, 2, 3]\nprint(id(list_a) == id(list_b))') == "False", "deck: two lists, two ids")
ok(shown('list_a = [1, 2, 3]\nlist_b = list_a\nprint(id(list_a) == id(list_b))') == "True", "deck: list_b = list_a, one id")
ok(shown('list_a = [1, 2, 3]\nb = id(list_a)\nlist_a[0] = 9\nprint(b == id(list_a))') == "True", "changing an item keeps the id")
ok(shown('list_a = [1, 2]\nb = id(list_a)\nlist_a += [6]\nprint(b == id(list_a))') == "True", "+= keeps the id")
ok(shown('list_a = [1, 2]\nb = list_a\nlist_a = list_a + [6]\nprint(id(b) == id(list_a))') == "False", "+ gives a new id")

# ---------- ids: never ask for an id number, and only compare ids of lists ----------
for q in Q.values():
    blob = repr({k: v for k, v in q.items() if k not in ("explain", "why", "trap", "hints")})
    ok(not re.search(r"\d{6,}", blob), f"{q['id']} shows an id number")
    codes = []
    if q.get("code"):
        codes.append((q["code"], ""))
    if q.get("scenario"):
        codes.append((C.BOSS_SCENARIO, ""))
    if q["type"] == "coding":
        codes += [(q["solution"], t["stdin"]) for t in q["challenge"]["tests"]]
    for code, stdin in codes:
        names = set(re.findall(r"\bid\((\w+)\)", code))
        if q["type"] == "msq":
            names |= {n for o in q["options"] for n in re.findall(r"\bid\((\w+)\)", o)}
        if not names:
            continue
        _, _, _, _, env = run(code if q["type"] != "fill" else code.replace("___", "playlist", 1).replace("___", "1"), stdin)
        ok(all(isinstance(env.get(n), list) for n in names), f"{q['id']} compares ids of something that is not a list: {names}")
for q in (Q["L3-4"],):
    _, _, _, _, env = run(q["setup"])
    names = {n for x in q["left"] for n in re.findall(r"\bid\((\w+)\)", x)}
    ok(names and all(isinstance(env[n], list) for n in names), "L3-4 compares ids of lists only")

# ---------- untaught features never appear in code students see or write ----------
UNTAUGHT = [r"\.append\(", r"\.extend\(", r"\.insert\(", r"\.pop\(", r"\.remove\(", r"\.sort\(", r"\.copy\(",
            r"\.split\(", r"\.join\(", r"\.index\(", r"\.count\(", r"\.reverse\(", r"\.clear\(", r"\bsorted\(",
            r"\bmin\(", r"\bmax\(", r"\bsum\(", r"\[[^\]\n]*:[^\]\n]*\]", r"\bis\b", r"\{", r"\blambda\b", r"\btry\s*:",
            r"\bexcept\b", r"\bf[\"']", r"\[[^\]\n]*\bfor\b", r"\bimport\b", r"\bdeepcopy\b", r"\.get\(", r"\bdict\(", r"\bset\("]


def code_parts(q):
    parts = []
    for k in ("code", "setup", "solution"):
        if q.get(k):
            parts.append(q[k])
    if q["type"] in ("order", "categorize"):
        parts += q["items"]
    if q["type"] == "match":
        parts += q["left"]
    if q["type"] in ("msq", "mcq") and all(re.match(r"^(print\(|\w+\s*\+?=)", o) for o in q["options"]):
        parts += q["options"]
    if q["type"] == "fill":
        parts += [b for acc in q["blanks"] for b in acc]
    if q["type"] == "coding":
        parts.append(q["challenge"]["starter"])
    return parts


for q in Q.values():
    blob = "\n".join(code_parts(q))
    ok(bool(blob) or q["type"] in ("tf", "ar", "msq", "mcq", "numeric", "predict"), f"{q['id']} has code to check")
    for pat in UNTAUGHT:
        ok(not re.search(pat, blob), f"{q['id']} uses untaught {pat}")
others = [l["demo"] for l in C.LEVELS] + [C.BOSS_SCENARIO, C.UI["lab_starter"]]
for i, code in enumerate(others):
    for pat in UNTAUGHT:
        ok(not re.search(pat, code), f"demo/lab {i} uses untaught {pat}")
ok(Q["L3-5"]["options"] and code_parts(Q["L3-5"])[-1] == Q["L3-5"]["options"][-1], "L3-5 options are scanned as code")

# ---------- metadata ----------
LEVELS_OK = {"Recall", "Read", "Implement", "Debug", "Extend", "Optimize", "Prompting"}
for q in Q.values():
    ok(q["level"] in LEVELS_OK and q["concept"] in C.CONCEPTS and q["type"] in C.TYPE_LABEL, f"{q['id']} metadata")
    ok(bool(q.get("hints")) and bool(q.get("explain")), f"{q['id']} hints/explain")
    ok(q["xp"] == C.XP[q["type"]], f"{q['id']} xp")
    ok(q["type"] not in ("land", "board"), f"{q['id']} uses a type from another mission")
    pub = public_question(q)
    ok(not ({"answer", "answers", "value", "blanks", "mapping", "line", "error", "why", "solution", "rules", "hints", "explain", "trap"} & set(pub)), f"{q['id']} public payload leaks a key")
    ok("₹" not in repr(q), f"{q['id']} uses the rupee sign")
    if q["type"] in ("mcq", "predict", "ar"):
        ok(0 <= q["answer"] < len(q["options"]), f"{q['id']} answer in range")
    if q["type"] == "msq":
        ok(q["answers"] and all(0 <= i < len(q["options"]) for i in q["answers"]) and len(q["answers"]) < len(q["options"]), f"{q['id']} answers in range")
    if q["type"] != "tf" and q["level"] not in ("Recall",) and q["type"] not in ("fill", "order", "match", "ar"):
        ok(bool(q.get("trap")), f"{q['id']} names its trap")
ok({q["level"] for q in Q.values()} == LEVELS_OK, "every cognitive level used")
ok({q["concept"] for q in Q.values()} == set(C.CONCEPTS), f"unused concepts {set(C.CONCEPTS) - {q['concept'] for q in Q.values()}}")
ok({q["type"] for q in Q.values()} == set(C.TYPE_LABEL), f"unused types {set(C.TYPE_LABEL) - {q['type'] for q in Q.values()}}")
ok(C.TOTAL == len(Q) == 28, f"TOTAL {C.TOTAL}")
ok(Q["L0-1"]["type"] == "mcq" and Q["L0-1"]["answer"] == 0, "L0-1 is an mcq keyed 0 (the generic tests need it)")
ok(Q["L0-2"]["type"] == "tf" and Q["L0-2"]["value"] is True, "L0-2 is a tf keyed True (the generic tests need it)")
ok(Q["L1-1"]["stage"] == "L1" and C.LEVEL_BY_ID["L1"]["main"][0] == "L1-1", "L1-1 opens L1")
ok(len(C.LEVEL_BY_ID["L0"]["main"]) + len(C.LEVEL_BY_ID["L1"]["main"]) >= 5, "L0 + L1 can earn the 5-in-a-row badge")
ok(set(C.STAGE_BADGE.values()) | {"combo-5", "clean-sweep", C.VISUAL_PRO[1]} == set(C.BADGES), "every badge can be earned")
ok(set(C.STAGE_BADGE) == {"L1", "L2", "L3", "L4", "L5", "BOSS"}, "a badge per stage")
ok(any(q["type"] == C.VISUAL_PRO[0] for q in Q.values()), "VISUAL_PRO type is used")
ok(C.AR_OPTIONS == S30.AR_OPTIONS and Q["L1-4"]["options"] == C.AR_OPTIONS, "AR options as in Session 30")
ok(set(S30.UI) <= set(C.UI) and C.UI["lab"] == "py" and C.UI["lab_name"] and C.UI["id"] == "wlists", f"UI keys {set(S30.UI) - set(C.UI)}")
ok("Your 3 jobs" in C.UI["story"] and C.UI["story"].count("<li>") == 3, "story has 3 jobs")
_, et, em, _, _ = run(C.UI["lab_starter"])
ok(et is None, f"lab starter runs: {et} {em}")
ok(shown(C.UI["lab_starter"]) == "True\nlist b : [1, 2, 6, 7]\nlist b : [1, 2, 6, 7]\nFalse", f"lab starter prints {shown(C.UI['lab_starter'])!r}")
keys = [k for k, _, _ in C.FEEDBACK_HELPED]
ok(len(set(keys)) == len(keys) and {"predict", "coding", "hints", "lab"} <= set(keys), "feedback options")
ok(all(k in C.TYPE_LABEL or k in ("lab", "hints", "xp") for k in keys), "feedback options are this mission's features")
ok(bool(C.FEEDBACK_TOPIC), "feedback topic")
ok("₹" not in repr(C.UI) + repr(C.LEVELS), "no rupee sign in the UI")
# Timers: the Session 30 rule (base + per line of code, with a floor); the 45-minute clock is the hard stop.
ok(C.MISSION_MINUTES == 45, "45-minute mission")
ok({k: v for k, v in S30.TIME.items() if k != "land"} == C.TIME and {k: v for k, v in S30.PER_LINE.items() if k != "land"} == C.PER_LINE
   and {k: v for k, v in S30.FLOOR.items() if k != "land"} == C.FLOOR, "TIME, PER_LINE and FLOOR as in Session 30")
for q in Q.values():
    ok(q["time"] == C.timer(q) == S30.timer(q) and q["time"] >= C.FLOOR.get(q["type"], 0), f"{q['id']} timer {q['time']} s")
ok(all(q["time"] == 360 for q in Q.values() if q["type"] == "coding"), "coding gets 6 minutes")
worst = sum(q["time"] for q in Q.values())
ok(45 * 60 <= worst <= 52 * 60, f"every timer used in full is {worst / 60:.1f} min: the clock, not the timers, ends a slow mission")

print(f"\n{N[0]} checks, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
