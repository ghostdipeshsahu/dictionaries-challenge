"""Built-in Functions: The Python Challenge · mission content (with Passing Mutable Objects).

Source of truth: the Built-in Functions deck (53 slides) and the teacher's key takeaways.
Story: Meera is the scorer for her hostel in the Inter-Hostel Cricket Cup. The batting order is
Teja, Ravi, Kiran, Sai, Divya with runs = [34, 0, 12, 51, 7].

Taught (and only this): a number passed to a function is immutable (a += 1 inside leaves the caller's a alone);
a list passed to a function is the same list (list_x += [3] changes the caller's list, list_x = list_x + [3]
does not); a default list is made once, when the function is defined ([3], [1, 2, 3], [3, 3]); recap:
positional, keyword and default arguments, a non-default argument cannot follow a default one (SyntaxError);
min() / max() of a sequence or of several values; strings compare character by character by unicode
(min("Python", "Java") is Java); sum(); sorted() returns a new list, sorted(..., reverse=True) high to low;
list(list_a) is an independent copy (list_b = list_a is not); list.reverse() flips in place and returns None;
all(), any(); reversed() walks a string or list backwards (list() shows it); enumerate() gives positions.
Code walkthrough: Extract Digits (C0d1n8 -> 9 0 8). Daily Challenge: squares of [2, 4, 1, 3, 5] in order.
Not used: list methods other than reverse(), dictionaries, comprehensions, lambda, key=, try/except, recursion.

Every expected output is checked against real Python by tests/verify_builtins.py.
"""

RUNS = "[34, 0, 12, 51, 7]"  # Teja, Ravi, Kiran, Sai, Divya

CONCEPTS = {
    "immutable_arg": "A number passed to a function",
    "mutable_arg": "A list passed to a function",
    "default_trap": "A list as a default argument",
    "arg_recap": "Positional, keyword and default arguments",
    "min": "min() finds the smallest",
    "min_str": "min() and max() with strings",
    "max": "max() finds the largest",
    "sum": "sum() adds up a sequence",
    "sorted": "sorted() returns a new list",
    "sorted_rev": "sorted() with reverse=True",
    "copy": "list() makes an independent copy",
    "reverse": "reverse() flips a list in place",
    "all": "all(): is every item true?",
    "any": "any(): is at least one item true?",
    "reversed": "reversed() for a string or a list",
    "enumerate": "enumerate() adds positions",
}

TYPE_LABEL = {
    "mcq": "Multiple choice", "msq": "Multiple select", "tf": "True or false",
    "ar": "Assertion and reasoning", "fill": "Fill in the blanks", "match": "Match the columns",
    "order": "Put in order", "categorize": "Sort into groups", "numeric": "Numeric answer",
    "predict": "Predict the output", "debug": "Debug mission", "coding": "Coding challenge",
}

ORDER = 2  # where this session sits in the course (session pickers list them in this order)
SLUG = "built-in-functions"  # this mission's URL: /built-in-functions/ (and /built-in-functions/teacher)
MISSION_MINUTES = 45  # the clock ends the mission here and the feedback opens (MISSION_MINUTES in the environment overrides it)

XP = {"mcq": 10, "tf": 10, "predict": 15, "msq": 15, "ar": 15, "fill": 15, "numeric": 15,
      "match": 20, "order": 20, "categorize": 20, "debug": 20, "coding": 40}
# Seconds per question. The Session 29 class ran out of time on 17 of 30 questions (coding solved by 4% in 3 minutes),
# so questions with code get time for every line to trace: base + per line, never less than the floor.
TIME = {"mcq": 40, "tf": 25, "predict": 30, "msq": 70, "ar": 60, "fill": 40, "numeric": 30,
        "match": 60, "order": 75, "categorize": 75, "debug": 45, "coding": 360}
PER_LINE = {"predict": 10, "numeric": 10, "fill": 10, "debug": 10, "match": 8}
FLOOR = {"predict": 45, "numeric": 45, "fill": 50, "debug": 60}


def timer(q):
    lines = sum(1 for line in (q.get("code") or "").splitlines() if line.strip())
    return max(FLOOR.get(q["type"], 0), TIME[q["type"]] + PER_LINE.get(q["type"], 0) * lines)

AR_OPTIONS = [
    "Both A and R are true, and R explains A",
    "Both A and R are true, but R does not explain A",
    "A is true, but R is false",
    "A is false, but R is true",
]

BADGES = {
    "run-finder": {"name": "Run Finder", "desc": "Clear Where Did the Runs Go?"},
    "score-keeper": {"name": "Score Keeper", "desc": "Clear Top Score, Low Score"},
    "board-builder": {"name": "Board Builder", "desc": "Clear The Leaderboard"},
    "over-checker": {"name": "Over Checker", "desc": "Clear Check the Over"},
    "bug-hunter": {"name": "Bug Hunter", "desc": "Clear Fix Meera's App"},
    "builtins-champion": {"name": "Built-in Functions Champion", "desc": "Win the final over"},
    "combo-5": {"name": "On Fire", "desc": "5 right answers in a row"},
    "clean-sweep": {"name": "Clean Sweep", "desc": "3 stars on any stage"},
    "sharp-eye": {"name": "Sharp Eye", "desc": "Every Debug mission right on the first try"},
}
STAGE_BADGE = {"L1": "run-finder", "L2": "score-keeper", "L3": "board-builder", "L4": "over-checker",
               "L5": "bug-hunter", "BOSS": "builtins-champion"}
VISUAL_PRO = ("debug", "sharp-eye")  # solving every question of this type first try earns this badge

BOSS_SCENARIO = '''def finish_over(score, balls):
    score += sum(balls)
    balls += [0]

score = 98
last_over = [4, 1, 6, 0, 2]
card = list(last_over)
finish_over(score, last_over)
print(score, len(last_over), len(card))
print(sorted(card, reverse=True))
print(all(card), any(card))'''

LEVELS = [
    {
        "id": "L0", "name": "Match Day", "difficulty": "Warm-up",
        "job": "Meet Meera's scorebook. When a friend writes in it, who sees the change?",
        "intel_title": "What you need to know",
        "intel": [
            "Hand a friend your <b>scorebook</b> and they write in <b>your</b> book. You see every change.",
            "Read out the <b>score</b> and they write it on their own notepad. Your book stays the same.",
            "Python works the same way. A <b>list</b> passed to a function is the scorebook. A <b>number</b> is the score read out.",
        ],
        "demo": 'def add_four(runs, over):\n    runs += 4\n    over += [4]\n\nruns = 52\nover = [1, 0]\nadd_four(runs, over)\nprint(runs, over)',
        "learn": ["Tell what a function can change and what it cannot", "Say why a list and a number behave differently"],
        "walk": [{"line": 2, "say": "runs is a number. += makes a new number, inside the function only."},
                 {"line": 3, "say": "over is a list. += adds to the same list the caller passed."},
                 {"line": 7, "say": "Pass the score and the over into the function."},
                 {"line": 8, "say": "The score is still 52. The over got the 4.", "shows": "52 [1, 0, 4]"}],
        "main": ["L0-1", "L0-2"],
    },
    {
        "id": "L1", "name": "Where Did the Runs Go?", "difficulty": "Easy",
        "job": "Runs vanish inside one of Meera's functions and pile up inside another. Find out which changes reach her list.",
        "intel_title": "What you need to know",
        "intel": [
            "A number is immutable: <code>runs += 4</code> inside a function changes nothing for the caller. A list is mutable: <code>over += [4]</code> changes the caller's list too, but <code>over = over + [4]</code> only points the parameter at a new list.",
            "A default list is made <b>once</b>, when the function is defined. <code>def add_four(over=[])</code> keeps one list for every call.",
            "Recap: a parameter with no default cannot come after one with a default. Python stops with <b>SyntaxError</b>.",
        ],
        "demo": 'def add_ball(balls):\n    balls += [6]\n\ndef new_ball(balls):\n    balls = balls + [6]\n\nover = [1, 0]\nadd_ball(over)\nprint(over)\nnew_ball(over)\nprint(over)',
        "learn": ["Predict what a function does to a number and to a list", "Tell += from = ... +", "Spot the default list trap"],
        "walk": [{"line": 2, "say": "+= adds to the same list the caller passed."},
                 {"line": 8, "say": "over goes in. balls and over are one list."},
                 {"line": 9, "say": "The 6 reached Meera's over.", "shows": "[1, 0, 6]"},
                 {"line": 5, "say": "+ builds a new list. Only balls points at it."},
                 {"line": 11, "say": "over has no second 6: the new list was thrown away.", "shows": "[1, 0, 6]"}],
        "main": ["L1-1", "L1-3", "L1-4", "L1-5"],
    },
    {
        "id": "L2", "name": "Top Score, Low Score", "difficulty": "Easy+",
        "job": "Find the top score, the lowest score and the team total for Meera's board, without writing a single loop.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>min(runs)</code> and <code>max(runs)</code> give the smallest and largest item; <code>min(3, 5, 4)</code> also works on separate values. <code>sum(runs)</code> adds up every number.",
            "Strings are compared character by character, by unicode value. <code>min(\"Python\", \"Java\")</code> is <code>'Java'</code>: J is 74, P is 80. Capital letters come before small ones.",
            "<code>max</code> is a name like any other. <code>max = max(runs)</code> hides the function, and the next <code>max(...)</code> fails.",
        ],
        "demo": f'runs = {RUNS}\nprint(min(runs), max(runs))\nprint(sum(runs))\nprint(min(3, 5, 4))\nprint(min("Python", "Java"))',
        "learn": ["Find the smallest and largest with min() and max()", "Add up a list with sum()", "Predict min() and max() on strings"],
        "walk": [{"line": 1, "say": "Teja 34, Ravi 0, Kiran 12, Sai 51, Divya 7."},
                 {"line": 2, "say": "Lowest and top score.", "shows": "0 51"},
                 {"line": 3, "say": "The team total.", "shows": "104"},
                 {"line": 4, "say": "min() also takes separate values.", "shows": "3"},
                 {"line": 5, "say": "J (74) comes before P (80).", "shows": "Java"}],
        "main": ["L2-1", "L2-2", "L2-3", "L2-5"],
    },
    {
        "id": "L3", "name": "The Leaderboard", "difficulty": "Medium",
        "job": "Build the leaderboard, high to low, and keep the batting order safe in a real backup.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>sorted(runs)</code> returns a new list, low to high, and <code>runs</code> keeps its order. <code>sorted(runs, reverse=True)</code> gives high to low: <code>reverse</code> is a default argument, False unless you pass it.",
            "<code>backup = list(runs)</code> makes an <b>independent copy</b>. <code>backup = runs</code> is only a second name for the same list.",
            "<code>runs.reverse()</code> flips the list <b>in place</b>. It gives back <code>None</code>, not a list.",
        ],
        "demo": f'runs = {RUNS}\nboard = sorted(runs, reverse=True)\nbackup = list(runs)\nruns.reverse()\nprint(board)\nprint(runs)\nprint(backup)',
        "learn": ["Sort into a new list, low to high or high to low", "Make an independent copy with list()", "Flip a list in place with reverse()"],
        "walk": [{"line": 2, "say": "A new list, high to low. runs is not changed."},
                 {"line": 3, "say": "A real backup: a second list with the same runs."},
                 {"line": 4, "say": "Flip runs itself, in place."},
                 {"line": 5, "say": "The leaderboard.", "shows": "[51, 34, 12, 7, 0]"},
                 {"line": 6, "say": "runs is flipped: Divya first, Teja last.", "shows": "[7, 51, 12, 0, 34]"},
                 {"line": 7, "say": "The backup kept the batting order.", "shows": "[34, 0, 12, 51, 7]"}],
        "main": ["L3-1", "L3-2", "L3-3", "L3-4", "L3-5"],
    },
    {
        "id": "L4", "name": "Check the Over", "difficulty": "Hard",
        "job": "Check each over: did every ball score? Was it a maiden? Then read the over backwards and number the batters.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>all(over)</code> is True when every item is true (0 counts as false). <code>any(over)</code> is True when at least one is, so <code>any(over)</code> False means a maiden over.",
            "<code>reversed(seq)</code> walks a string or a list from the end. Wrap it in <code>list()</code> to see it as a list.",
            "<code>enumerate(names)</code> gives each position with its item: <code>for i, name in enumerate(names):</code>. Positions start at 0.",
        ],
        "demo": 'over = [1, 0, 4]\nprint(all(over), any(over))\nprint(list(reversed(over)))\nfor i, run in enumerate(over):\n    print(i, run)',
        "learn": ["Check every item with all() and at least one with any()", "Reverse a string or a list with reversed()", "Get positions with enumerate()"],
        "walk": [{"line": 2, "say": "The 0 is false, so all() is False. The 1 and the 4 are true, so any() is True.", "shows": "False True"},
                 {"line": 3, "say": "The same balls, last one first.", "shows": "[4, 0, 1]"},
                 {"line": 4, "say": "enumerate() gives a position and a ball each time."},
                 {"line": 5, "say": "Positions start at 0.", "shows": "0 1\n1 0\n2 4"}],
        "main": ["L4-1", "L4-2", "L4-3", "L4-4"],
    },
    {
        "id": "L5", "name": "Fix Meera's App", "difficulty": "Hard",
        "job": "Meera's batting card only prints the names. Extend it so it works for every team, not just the examples.",
        "intel_title": "Before you start",
        "intel": [
            "Your code reads input and prints. Sample tests show the output; hidden tests try tricky cases, like only one batter or a full team of 11.",
            "The check also looks at <b>how</b> you solved it: the card must really use <code>enumerate()</code>.",
        ],
        "demo": 'notes = "1W4.6"\nruns = []\nfor ch in notes:\n    if ch in "0123456789":\n        runs += [int(ch)]\nprint(sum(runs), min(runs), max(runs))',
        "learn": ["Pick the digits out of a string", "Use sum(), min() and max() on what you collect", "Number a list with enumerate()"],
        "walk": [{"line": 1, "say": "Meera's notes for an over: W is a wicket, . is a dot ball."},
                 {"line": 4, "say": "Keep only the characters that are digits."},
                 {"line": 5, "say": "int() turns the digit into a number before it goes in the list."},
                 {"line": 6, "say": "Runs 1, 4 and 6.", "shows": "11 1 6"}],
        "main": ["L5-2"],
    },
    {
        "id": "BOSS", "name": "The Final Over", "difficulty": "Boss",
        "job": "The last over of the final. Everything comes together: functions, copies, the leaderboard and the over report.",
        "intel_title": "Before you start",
        "intel": [
            "Read the program on the left line by line. For each line, ask: does it change a list, make a new one, or only read it?",
            "Last two jobs: tell an AI exactly what you want, then spot what its code gets wrong.",
        ],
        "demo": BOSS_SCENARIO,
        "learn": ["Trace functions, copies and built-ins together", "Fix and rewrite real programs", "Write a spec an AI can follow"],
        "walk": [{"line": 2, "say": "score is a number: this changes only the function's own score."},
                 {"line": 3, "say": "balls is Meera's list: the 0 is added to last_over itself."},
                 {"line": 7, "say": "card is a real copy, made before the call."},
                 {"line": 9, "say": "score is still 98. last_over has 6 balls, card still has 5.", "shows": "98 6 5"},
                 {"line": 10, "say": "The card's balls, high to low.", "shows": "[6, 4, 2, 1, 0]"},
                 {"line": 11, "say": "One dot ball: not all. Some runs: any.", "shows": "False True"}],
        "main": ["B-1", "B-2", "B-3", "B-4", "B-5"],
    },
]

# ---------------------------------------------------------------------------------------------
Q = []


def add(**q):
    q.setdefault("xp", XP[q["type"]])
    q.setdefault("time", timer(q))
    Q.append(q)


# ---------- L0 · Match Day ----------
add(id="L0-1", stage="L0", type="mcq", level="Recall", concept="mutable_arg",
    title="Meera hands her scorebook to Ravi. He writes a 4 for the next ball and gives it back. What does Meera see?",
    options=["The 4 is in her scorebook", "No 4: Ravi wrote in a copy", "Two scorebooks, one with the 4", "An error: only Meera can write in it"],
    answer=0,
    why={1: "Ravi got the <b>same</b> book, not a copy. His 4 is in it.",
         2: "There is only one scorebook. Nobody made a second one.",
         3: "Anyone holding the book can write in it."},
    hints=["How many scorebooks are there?"],
    explain="Ravi wrote in Meera's <b>own</b> book, so she sees the 4. A list passed to a function works the same way: <code>over += [4]</code> inside the function changes the caller's list.",
    trap="Thinking the friend gets a separate copy.")

add(id="L0-2", stage="L0", type="tf", level="Recall", concept="immutable_arg",
    title="True or false: Meera reads out the team score, 52. Kiran adds 4 on his own notepad. Meera's scorebook still says 52.",
    value=True,
    hints=["Kiran wrote on his notepad. Did he touch Meera's book?"],
    explain="Kiran only changed his own note. A number passed to a function is like this: <code>runs += 4</code> inside makes a new number there, and the caller's <code>runs</code> stays 52.")

# ---------- L1 · Where Did the Runs Go? ----------
add(id="L1-1", stage="L1", type="numeric", level="Read", concept="immutable_arg",
    title="What number does this print?",
    code='def add_four(runs):\n    runs += 4\n\nruns = 52\nadd_four(runs)\nprint(runs)',
    value=52,
    hints=["A number cannot change. What does runs += 4 do inside the function?"],
    explain="Inside the function, <code>runs += 4</code> makes a new number, 56, for the function's own <code>runs</code>. The <code>runs</code> outside still points at 52.",
    trap="Answering 56, as if the function had changed the outside runs.")

add(id="L1-3", stage="L1", type="categorize", level="Read", concept="mutable_arg",
    title="Each f(over) is called on over = [1, 0]. What does print(over) show afterwards?",
    items=["def f(x): x += [4]", "def f(x): x = x + [4]", "def f(x): x[0] = 4", "def f(x): x = [4]", "def f(x): y = x; y += [4]"],
    categories=["[1, 0, 4]", "[1, 0]", "[4, 0]"],
    mapping=[0, 1, 2, 1, 0],
    setup="over = [1, 0]",
    hints=["Ask of each line: does it change the list, or point x at a new list?", "x = ... only moves the name x. += and x[0] = change the list itself."],
    explain="<code>+=</code> and <code>x[0] = 4</code> change the one list, so Meera sees it. <code>x = x + [4]</code> and <code>x = [4]</code> only point <code>x</code> at a new list. <code>y = x</code> is a second name for the same list, so <code>y += [4]</code> reaches it too.",
    trap="<code>x = x + [4]</code> looks like <code>x += [4]</code>, but it builds a new list.")

add(id="L1-4", stage="L1", type="predict", level="Read", concept="default_trap",
    title="add_four() has a default list. What does this print?",
    code='def add_four(over=[]):\n    over += [4]\n    print(over)\n\nadd_four()\nadd_four([1, 2])\nadd_four()',
    options=["[4]\n[1, 2, 4]\n[4, 4]", "[4]\n[1, 2, 4]\n[4]", "[4]\n[1, 2, 4]\n[1, 2, 4, 4]", "[4]\n[4]\n[4]"],
    answer=0,
    why={1: "The default list is made <b>once</b>, when the function is defined. The first call already put a 4 in it.",
         2: "<code>[1, 2]</code> is a different list, given only to the second call. The default list never saw it.",
         3: "The second call gets <code>[1, 2]</code>, so it prints <code>[1, 2, 4]</code>."},
    hints=["When is the empty list [] made: at every call, or once?", "Which calls use the default list?"],
    explain="Default arguments are evaluated <b>once</b>, when the function is defined. Calls 1 and 3 share that one list: <code>[4]</code>, then <code>[4, 4]</code>. Call 2 brings its own list: <code>[1, 2, 4]</code>.",
    trap="Expecting a fresh empty list at every call.")

add(id="L1-5", stage="L1", type="debug", level="Debug", concept="arg_recap",
    title="Meera's score_line() will not even start. Tap the line where Python stops, then choose what goes wrong.",
    code='def score_line(name="Meera", runs):\n    print(name, runs)\n\nscore_line(runs=52)',
    errors=["SyntaxError: non-default argument follows default argument", "TypeError: score_line() missing 1 required positional argument: 'name'",
            "It prints Meera 52", "NameError: name 'runs' is not defined"],
    line=1, error=0, focus=1,
    hints=["Look at the order of the parameters in the def line.", "Can a parameter with no default come after one that has a default?"],
    explain="<code>runs</code> has no default but comes after <code>name=\"Meera\"</code>. Python refuses the def line before anything runs: <code>SyntaxError</code>. Put the default last: <code>def score_line(runs, name=\"Meera\"):</code>.",
    trap="Thinking the keyword call <code>runs=52</code> makes it fine.")

# ---------- L2 · Top Score, Low Score ----------
add(id="L2-1", stage="L2", type="numeric", level="Read", concept="sum",
    title="What number does this print?",
    code=f'runs = {RUNS}\nprint(sum(runs) - max(runs))',
    value=53,
    hints=["Add up all five scores first, then take away the top one."],
    explain="<code>sum(runs)</code> is 34 + 0 + 12 + 51 + 7 = 104. <code>max(runs)</code> is 51. 104 - 51 = 53.",
    trap="Forgetting Ravi's 0 still counts as an item, or adding wrongly.")

add(id="L2-2", stage="L2", type="match", level="Read", concept="min",
    title="Match each expression to its value.",
    code=f'runs = {RUNS}',
    left=["min(runs)", "max(runs)", "sum(runs)", "min(34, 12, 51)", "max(7, 34)"],
    right=["34", "104", "0", "12", "51"],
    mapping=[2, 4, 1, 3, 0],
    setup=f'runs = {RUNS}',
    hints=["min() and max() work on a list or on separate values.", "sum() adds every item."],
    explain="The lowest is Ravi's 0 and the top is Sai's 51. The total is 104. With separate values, <code>min(34, 12, 51)</code> is 12 and <code>max(7, 34)</code> is 34.")

add(id="L2-3", stage="L2", type="predict", level="Read", concept="min_str",
    title="min() and max() on names. What does this print?",
    code='names = ["Teja", "Kiran", "Ravi"]\nprint(min(names))\nprint(max(names))',
    options=["Kiran\nTeja", "Teja\nKiran", "Teja\nRavi", "Ravi\nTeja"],
    answer=0,
    why={1: "Strings are not compared by length. They are compared letter by letter.",
         2: "min() and max() do not pick the first and last items. They compare them.",
         3: "K comes before R, so Kiran is the smallest."},
    hints=["Compare the first letters: T, K, R. Which comes first in unicode?"],
    explain="Strings are compared character by character by unicode value. K (75) &lt; R (82) &lt; T (84), so <code>min</code> is Kiran and <code>max</code> is Teja.",
    trap="Comparing the names by length.")

add(id="L2-5", stage="L2", type="debug", level="Debug", concept="max",
    title="Meera saves the top score in a variable named max. Day two crashes. Tap the line where Python stops, then choose what goes wrong.",
    code=f'runs = {RUNS}\nmax = max(runs)\nprint("Top score:", max)\nday_two = [8, 60, 15]\nprint("Top score:", max(day_two))',
    errors=["TypeError: 'int' object is not callable", "It prints Top score: 60", "NameError: name 'max' is not defined", "ValueError"],
    line=5, error=0, focus=2,
    hints=["After line 2, what is max: the function, or a number?"],
    explain="Line 2 points the name <code>max</code> at the number 51, so the function is hidden. On line 5, <code>max(day_two)</code> tries to call 51 like a function: <code>TypeError: 'int' object is not callable</code>. Name the variable <code>top</code> instead.",
    trap="Blaming line 4. The list is fine; the name max is the problem.")

# ---------- L3 · The Leaderboard ----------
add(id="L3-1", stage="L3", type="predict", level="Read", concept="sorted",
    title="What does this print?",
    code=f'runs = {RUNS}\nboard = sorted(runs)\nprint(board)\nprint(runs)',
    options=["[0, 7, 12, 34, 51]\n[34, 0, 12, 51, 7]", "[0, 7, 12, 34, 51]\n[0, 7, 12, 34, 51]",
             "None\n[0, 7, 12, 34, 51]", "[51, 34, 12, 7, 0]\n[34, 0, 12, 51, 7]"],
    answer=0,
    why={1: "<code>sorted()</code> makes a <b>new</b> list. The old one keeps the batting order.",
         2: "<code>sorted()</code> returns the new list, so board is not None.",
         3: "Without <code>reverse=True</code>, sorted() goes from low to high."},
    hints=["Does sorted() change runs, or give back a new list?"],
    explain="<code>sorted(runs)</code> returns a new list from low to high, and <code>runs</code> is left in the batting order.",
    trap="Thinking sorted() changes the list you give it.")

add(id="L3-2", stage="L3", type="fill", level="Implement", concept="sorted_rev",
    title="Fill the gaps so Meera's leaderboard prints high to low: [51, 34, 12, 7, 0].",
    code=f'runs = {RUNS}\nboard = ___(runs, ___=True)\nprint(board)',
    blanks=[["sorted"], ["reverse"]],
    expect="[51, 34, 12, 7, 0]",
    hints=["Which built-in returns a new, ordered list?", "Which keyword argument flips the order?"],
    explain="<code>sorted(runs, reverse=True)</code> returns a new list from high to low. <code>reverse</code> is a keyword argument here.")

add(id="L3-3", stage="L3", type="ar", level="Read", concept="arg_recap",
    title="Read the assertion and the reason.",
    assertion="sorted(runs) gives the runs from low to high, even though we did not pass reverse.",
    reason="reverse is a default argument of sorted(), and its default value is False.",
    options=AR_OPTIONS, answer=0,
    why={1: "R is exactly why A happens: with no reverse given, the default False is used.",
         2: "R is true: sorted(sequence, reverse=False) is how sorted() is defined.",
         3: "A is true: sorted(runs) is low to high."},
    hints=["What value does a default argument take when you leave it out?"],
    explain="Both are true and R explains A. When you leave out <code>reverse</code>, its default <code>False</code> is used, so the order is low to high. <code>reverse=True</code> is a keyword argument that changes it.")

add(id="L3-4", stage="L3", type="order", level="Implement", concept="copy",
    title="Put the lines in order so the program prints [34, 0, 12, 9], then [34, 0, 12].",
    items=["runs += [9]", "print(backup)", "backup = list(runs)", "runs = [34, 0, 12]", "print(runs)"],
    mapping=[3, 2, 0, 4, 1],
    expect="[34, 0, 12, 9]\n[34, 0, 12]",
    hints=["The backup must be made before the 9 arrives.", "Which list is printed first?"],
    explain="Make the list, copy it with <code>list(runs)</code>, then add the 9 to runs only. The copy is a separate list, so it keeps <code>[34, 0, 12]</code>.")

add(id="L3-5", stage="L3", type="categorize", level="Read", concept="reverse",
    title="Each line starts from runs = [34, 0, 12]. What does print(runs) show after it?",
    items=["runs.reverse()", "board = sorted(runs, reverse=True)", "back = list(runs); back.reverse()",
           "same = runs; same.reverse()", "runs = runs.reverse()"],
    categories=["[34, 0, 12]", "[12, 0, 34]", "None"],
    mapping=[1, 0, 0, 1, 2],
    setup="runs = [34, 0, 12]",
    hints=["reverse() flips the list it is called on, in place.", "What does reverse() give back?"],
    explain="<code>runs.reverse()</code> flips runs itself, and so does <code>same.reverse()</code>, because same is the same list. sorted() and a <code>list()</code> copy leave runs alone. <code>reverse()</code> gives back <code>None</code>, so <code>runs = runs.reverse()</code> points runs at None.",
    trap="Writing <code>runs = runs.reverse()</code> and losing the list.")

# ---------- L4 · Check the Over ----------
add(id="L4-1", stage="L4", type="predict", level="Read", concept="all",
    title="What does this print?",
    code='over = [1, 0, 4, 6, 0, 2]\nprint(all(over))\nprint(any(over))',
    options=["False\nTrue", "True\nTrue", "False\nFalse", "True\nFalse"],
    answer=0,
    why={1: "0 counts as false. One dot ball is enough to make <code>all()</code> False.",
         2: "1, 4, 6 and 2 are true, so at least one item is true: <code>any()</code> is True.",
         3: "The other way round: all() needs every item, any() needs just one."},
    hints=["Which number counts as false?"],
    explain="0 is false, so <code>all(over)</code> is False: not every ball scored. Other balls are true, so <code>any(over)</code> is True.",
    trap="Thinking all() just checks that the list has items.")

add(id="L4-2", stage="L4", type="mcq", level="Recall", concept="any",
    title="A maiden over has no runs at all. For which over is any(over) False?",
    options=["[0, 1, 0, 0, 0, 0]", "[6, 6, 6, 6, 6, 6]", "[0, 0, 0, 0, 0, 0]", "[4, 0, 0, 0, 0, 0]"],
    answer=2,
    why={0: "The 1 is true, so any() finds it: True.",
         1: "Every 6 is true: any() is True.",
         3: "The 4 is true, so any() is True."},
    hints=["any() is False only when no item is true."],
    explain="Only an over of all zeros has no true item, so <code>any(over)</code> is False: a maiden. One run anywhere makes it True.",
    trap="Thinking any() looks at the first ball only.")

add(id="L4-3", stage="L4", type="numeric", level="Read", concept="enumerate",
    title="What number does this print?",
    code='names = ["Teja", "Ravi", "Kiran", "Sai"]\nfor i, name in enumerate(names):\n    if name == "Kiran":\n        print(i)',
    value=2,
    hints=["enumerate() starts counting at 0."],
    explain="enumerate() gives (0, Teja), (1, Ravi), (2, Kiran), (3, Sai). Kiran's position is 2.",
    trap="Answering 3, counting from 1 like on the scorecard.")

add(id="L4-4", stage="L4", type="predict", level="Read", concept="reversed",
    title="Meera reads a name and an over backwards. What does this print?",
    code='name = "Teja"\nback = ""\nfor ch in reversed(name):\n    back += ch\nprint(back)\nprint(list(reversed([1, 0, 4])))',
    options=["ajeT\n[4, 0, 1]", "Teja\n[4, 0, 1]", "ajeT\n[4, 1, 0]", "ajeT\n[1, 0, 4]"],
    answer=0,
    why={1: "reversed() works on strings too: the loop gets a, j, e, T.",
         2: "reversed() does not sort. It only flips the order: last item first.",
         3: "list(reversed(...)) gives the items from the end."},
    hints=["reversed() gives the last character first.", "Does reversed() sort, or only flip?"],
    explain="<code>reversed(name)</code> gives a, j, e, T, and <code>+=</code> joins them: <code>ajeT</code>. <code>list(reversed([1, 0, 4]))</code> flips the list: <code>[4, 0, 1]</code>.",
    trap="Mixing up reversed() with sorted(..., reverse=True).")

# ---------- L5 · Fix Meera's App ----------
add(id="L5-2", stage="L5", type="coding", level="Extend", concept="enumerate",
    challenge={
        "title": "Batting Card",
        "statement": "Meera prints the batting card. The starter only prints the names. Extend it: each line must show the batter's <b>number</b> (starting at 1), the <b>name</b> and the <b>runs</b>, like <code>1 Teja 34</code>.",
        "input_fmt": "First line: the names in batting order. Second line: their runs, in the same order.",
        "output_fmt": "One line per batter: number, name and runs.",
        "starter": 'names = input().split()\nruns = input().split()\nfor name in names:\n    print(name)\n',
        "tests": [
            {"stdin": "Teja Ravi Kiran\n34 0 12", "expected": "1 Teja 34\n2 Ravi 0\n3 Kiran 12"},
            {"stdin": "Sai Divya\n51 7", "expected": "1 Sai 51\n2 Divya 7"},
            {"stdin": "Teja\n0", "expected": "1 Teja 0", "hidden": True, "note": "only one batter"},
            {"stdin": "Teja Ravi Kiran Sai Divya Anu Rahul Priya Arjun Neha Vikram\n34 0 12 51 7 22 9 15 3 0 1",
             "expected": "1 Teja 34\n2 Ravi 0\n3 Kiran 12\n4 Sai 51\n5 Divya 7\n6 Anu 22\n7 Rahul 9\n8 Priya 15\n9 Arjun 3\n10 Neha 0\n11 Vikram 1",
             "hidden": True, "note": "a full team of 11"},
        ],
    },
    rules=[{"require": r"enumerate\s*\(", "msg": "Use enumerate() to get each batter's number."}],
    solution='names = input().split()\nruns = input().split()\nfor i, name in enumerate(names):\n    print(i + 1, name, runs[i])\n',
    hints=["enumerate(names) gives a position and a name each time.", "Positions start at 0: print i + 1. The same position finds the runs: runs[i]."],
    explain="<code>for i, name in enumerate(names):</code> gives each position with its name. <code>i + 1</code> is the card number, and <code>runs[i]</code> is that batter's runs, because both lists are in batting order.",
    trap="Printing <code>i</code> instead of <code>i + 1</code>: the card would start at 0.")

# ---------- Final Boss ----------
add(id="B-1", stage="BOSS", type="predict", level="Read", concept="copy", scenario=True,
    title="Run the scenario on the left. What does it print?",
    options=["98 6 5\n[6, 4, 2, 1, 0]\nFalse True", "111 6 5\n[6, 4, 2, 1, 0]\nFalse True",
             "98 6 6\n[6, 4, 2, 1, 0, 0]\nFalse True", "98 5 5\n[6, 4, 2, 1, 0]\nTrue True"],
    answer=0,
    why={1: "score is a number. <code>score += sum(balls)</code> changes only the function's own score.",
         2: "card is a <code>list()</code> copy made before the call. The 0 went into last_over only.",
         3: "balls is Meera's last_over itself, so it gets the 0. And card has a 0, so all() is False."},
    hints=["Which names point at a list, and which at a number?", "card was copied before the call."],
    explain="The number <code>score</code> is untouched: 98. <code>balls += [0]</code> adds to last_over itself: 6 balls. card is an independent copy with 5 balls, sorted high to low. It has a 0, so <code>all()</code> is False, and runs, so <code>any()</code> is True.",
    trap="Thinking the function's <code>score += ...</code> reaches the outside score.")

add(id="B-2", stage="BOSS", type="msq", level="Debug", concept="sorted",
    title="Daily Challenge from class: this should print the squares in increasing order, [1, 4, 9, 16, 25]. Which single changes make it print exactly that?",
    code='list_a = [2, 4, 1, 3, 5]\nlist_x = []\nfor item in list_a:\n    list_x += [item * item]\nprint(list_x)',
    options=["Line 1: list_a = sorted([2, 4, 1, 3, 5])", "Line 3: for item in sorted(list_a):", "Line 3: for item in reversed(list_a):",
             "Line 5: print(sorted(list_x))", "Line 5: print(list_x.reverse())"],
    answers=[0, 1, 3],
    hints=["Now it prints [4, 16, 1, 9, 25]: the squares follow the list's order.", "You can sort the numbers before squaring, or the squares at the end."],
    explain="The program squares in the list's own order: <code>[4, 16, 1, 9, 25]</code>. Sorting <code>list_a</code> first, looping over <code>sorted(list_a)</code>, or printing <code>sorted(list_x)</code> all give <code>[1, 4, 9, 16, 25]</code>. reversed() only flips the order, and <code>reverse()</code> gives back None.",
    trap="Using reversed() as if it sorted.")

add(id="B-3", stage="BOSS", type="coding", level="Optimize", concept="all",
    challenge={
        "title": "Over Report",
        "statement": "Meera's over report checks every ball by hand, and it is wrong for some overs. Rewrite it with <b>sum()</b>, <b>all()</b> and <b>any()</b>. The output must stay exactly the same, and be right for every over.",
        "input_fmt": "One line: the runs off each ball, separated by spaces (at least one ball).",
        "output_fmt": "Three lines: Runs: the total; Every ball scored: True or False; Maiden: True if no ball scored.",
        "starter": 'over = input().split()\nruns = 0\nevery_ball = True\nmaiden = True\nfor ball in over:\n    runs = runs + int(ball)\n    if int(ball) == 0:\n        every_ball = False\n    else:\n        every_ball = True\n    if int(ball) > 0:\n        maiden = False\nprint("Runs:", runs)\nprint("Every ball scored:", every_ball)\nprint("Maiden:", maiden)\n',
        "tests": [
            {"stdin": "1 0 4 6 0 0", "expected": "Runs: 11\nEvery ball scored: False\nMaiden: False"},
            {"stdin": "1 2 4 6 1 1", "expected": "Runs: 15\nEvery ball scored: True\nMaiden: False"},
            {"stdin": "0 4 4 4 4 4", "expected": "Runs: 20\nEvery ball scored: False\nMaiden: False", "hidden": True, "note": "a dot ball first"},
            {"stdin": "0 0 0 0 0 0", "expected": "Runs: 0\nEvery ball scored: False\nMaiden: True", "hidden": True, "note": "a maiden over"},
            {"stdin": "6 6 0 6 6 6", "expected": "Runs: 30\nEvery ball scored: False\nMaiden: False", "hidden": True, "note": "a dot ball in the middle"},
        ],
    },
    rules=[
        {"require": r"\bsum\s*\(", "msg": "Use sum() for the runs."},
        {"require": r"\ball\s*\(", "msg": "Use all() to check every ball."},
        {"require": r"\bany\s*\(", "msg": "Use any() for the maiden check."},
        {"forbid": r"\bif\b", "msg": "Let sum(), all() and any() do the checking: no if needed."},
    ],
    solution='over = []\nfor ball in input().split():\n    over += [int(ball)]\nprint("Runs:", sum(over))\nprint("Every ball scored:", all(over))\nprint("Maiden:", not any(over))\n',
    hints=["Build a list of numbers first: over += [int(ball)].", "Every ball scored is all(over). A maiden means no ball scored: not any(over)."],
    explain="The starter's <code>else: every_ball = True</code> undoes an earlier dot ball, so only the last ball counts. With a list of numbers, <code>all(over)</code> checks every ball and <code>not any(over)</code> finds a maiden, with no flags to get wrong.",
    trap="Calling all() on the strings from split(): \"0\" is a non-empty string, so it counts as true.")

add(id="B-4", stage="BOSS", type="msq", level="Prompting", concept="mutable_arg",
    title="You ask an AI for top_score(runs), which gives back the highest score. Which lines must your spec include so its code is right?",
    options=["It takes one list of whole-number scores and returns the highest one.",
             "It must not change the list it is given: the batting order stays.",
             "Example: top_score([34, 0, 12]) returns 34.",
             "If every score is 0, it returns 0.",
             "Make it fast and smart.",
             "Put the list in order first, then take the last item."],
    answers=[0, 1, 2, 3],
    hints=["A good spec gives the input, the output, an example and the edge case. Wishes give the AI nothing to check."],
    explain="The AI needs what goes in and comes out, the rule that Meera's list stays unchanged (a list passed in can be changed by the function), a checkable example and the all-zero case. \"Fast and smart\" changes nothing, and reordering the list is exactly what must not happen.",
    trap="Forgetting to say the list must not change: a function can change a list passed to it.")

add(id="B-5", stage="BOSS", type="debug", level="Prompting", concept="default_trap",
    title="An AI wrote new_over() to start a fresh over with one ball. second should be [6]. Tap the line that causes the bug, then choose what goes wrong.",
    code='def new_over(ball, over=[]):\n    over += [ball]\n    return over\n\nfirst = new_over(4)\nsecond = new_over(6)\nprint(second)',
    errors=["It prints [4, 6]: both calls share one default list", "It prints [6]",
            "TypeError: new_over() missing 1 required positional argument: 'over'", "It prints [4]"],
    line=1, error=0, focus=1,
    hints=["When is the default list made?", "Both calls leave out over. Which list do they get?"],
    explain="The default <code>[]</code> on line 1 is made once, when the function is defined. Both calls share it, so the 6 joins the 4: <code>[4, 6]</code>. Make the list inside the function instead: <code>def new_over(ball):</code> then <code>over = [ball]</code>.",
    trap="Trusting a default list to start empty at every call.")

QUESTIONS = {q["id"]: q for q in Q}
LEVEL_IDS = [lvl["id"] for lvl in LEVELS]
LEVEL_BY_ID = {lvl["id"]: lvl for lvl in LEVELS}
TOTAL = sum(len(lvl["main"]) for lvl in LEVELS)

GUIDE_HTML = """<h3>Passing values to a function</h3>
    <div class="tscroll"><table><thead><tr><th>Inside the function</th><th>Passed in</th><th>The caller sees</th></tr></thead><tbody>
      <tr><td><code>runs += 4</code></td><td>a number (immutable)</td><td>no change: a new number is made inside</td></tr>
      <tr><td><code>over += [4]</code></td><td>a list (mutable)</td><td><b>changed</b>: it is the same list</td></tr>
      <tr><td><code>over = over + [4]</code></td><td>a list</td><td>no change: a new list, only inside</td></tr>
      <tr><td><code>def f(over=[])</code></td><td>nothing</td><td>one default list, made <b>once</b>, shared by every call</td></tr></tbody></table></div>
    <h3>Built-in functions · runs = [34, 0, 12, 51, 7]</h3>
    <div class="tscroll"><table><thead><tr><th>Code</th><th>Gives</th></tr></thead><tbody>
      <tr><td><code>min(runs)</code> · <code>min(3, 5, 4)</code></td><td><code>0</code> · <code>3</code></td></tr>
      <tr><td><code>max(runs)</code></td><td><code>51</code></td></tr>
      <tr><td><code>sum(runs)</code></td><td><code>104</code></td></tr>
      <tr><td><code>min("Python", "Java")</code></td><td><code>'Java'</code>: letter by letter, by unicode (capitals first)</td></tr>
      <tr><td><code>sorted(runs)</code></td><td>a <b>new</b> list <code>[0, 7, 12, 34, 51]</code>; runs unchanged</td></tr>
      <tr><td><code>sorted(runs, reverse=True)</code></td><td><code>[51, 34, 12, 7, 0]</code></td></tr>
      <tr><td><code>list(runs)</code></td><td>an independent copy (<code>b = runs</code> is only a second name)</td></tr>
      <tr><td><code>runs.reverse()</code></td><td>flips runs <b>in place</b>; gives back <code>None</code></td></tr>
      <tr><td><code>list(reversed(runs))</code></td><td><code>[7, 51, 12, 0, 34]</code>; works on strings too</td></tr></tbody></table></div>
    <h3>Checking and counting · over = [1, 0, 4]</h3>
    <div class="tscroll"><table><thead><tr><th>Code</th><th>Gives</th></tr></thead><tbody>
      <tr><td><code>all(over)</code></td><td><code>False</code>: True only if <b>every</b> item is true (0 is false)</td></tr>
      <tr><td><code>any(over)</code></td><td><code>True</code>: True if <b>at least one</b> item is true</td></tr>
      <tr><td><code>for i, run in enumerate(over):</code></td><td><code>0 1</code>, <code>1 0</code>, <code>2 4</code>: positions start at 0</td></tr></tbody></table></div>
    <h3>Remember</h3>
    <ul><li>A parameter with no default cannot follow one with a default: <b>SyntaxError</b>.</li>
      <li>Never name a variable <code>max</code>, <code>min</code> or <code>sum</code>: the function is hidden and the next call fails.</li>
      <li>Digits read from a string are strings. Use <code>int(ch)</code> before <code>sum()</code>.</li>
      <li><code>runs = runs.reverse()</code> loses the list: reverse() gives back None.</li></ul>"""

LAB_STARTER = f'''runs = {RUNS}
print(min(runs), max(runs), sum(runs))
print(sorted(runs, reverse=True))
over = [1, 0, 4]
print(all(over), any(over))
for i, name in enumerate(["Teja", "Ravi", "Kiran"]):
    print(i + 1, name)
'''

UI = {
    "id": "builtins",
    "title": "Built-in Functions: The Python Challenge",
    "short": "Built-in Functions",
    "hero_h1": "Mission: <em>Fix the Cricket Scoreboard</em>",
    "hero_p": "It is the final of the Inter-Hostel Cricket Cup, and Meera is the scorer. Her Python scoring app is acting up: runs vanish inside functions, the leaderboard comes out wrong, and the over report lies. Fix it with Python's built-in functions, one stage at a time.",
    "story": """<p><b>It is the final of the Inter-Hostel Cricket Cup.</b> Meera keeps the score in a Python app. Now it is a mess: runs vanish inside functions, the leaderboard comes out wrong, and the over report lies.</p>
      <h3>Your 3 jobs</h3>
      <ol><li>🏏 <b>Find the missing runs.</b> Which changes inside a function reach Meera's list, and which do not?</li>
        <li>📊 <b>Build the scoreboard.</b> Top score, lowest score, total and a leaderboard, with min(), max(), sum() and sorted().</li>
        <li>✅ <b>Check every over.</b> Did every ball score? Was it a maiden? Number the batters.</li></ol>
      <p class="win">You win when every stage is cleared and the final over is scored.</p>""",
    "lab": "py",
    "lab_name": "Function Lab",
    "lab_starter": LAB_STARTER,
    "lab_tips": [
        'Run it first. Is <code>runs</code> still in batting order after <code>sorted()</code>?',
        'Add <code>runs.reverse()</code> and print <code>runs</code>. How is that different from <code>sorted(runs, reverse=True)</code>?',
        'Change <code>over</code> to <code>[0, 0, 0]</code>. What do <code>all()</code> and <code>any()</code> say now?',
        'Write <code>def add(score, card=[]):</code> that does <code>card += [score]</code> and prints <code>card</code>. Call it twice.',
        'Try <code>min("Python", "Java")</code> and <code>min("apple", "Banana")</code>. Can you explain the second?',
    ],
    "boss_win": "Scoreboard fixed!",
    "champion": "Built-in Functions Champion",
    "guide_title": "Field guide: built-in functions",
    "guide_html": GUIDE_HTML,
}

assert len(QUESTIONS) == len(Q), "duplicate question id"
assert TOTAL == len(Q) == 25, TOTAL
for lvl in LEVELS:
    for qid in lvl["main"]:
        assert QUESTIONS[qid]["stage"] == lvl["id"], qid

# End-of-mission feedback: "What helped you learn the most?" (key, emoji, label)
FEEDBACK_HELPED = [
    ("predict", "🔮", "Predict-the-output questions"),
    ("categorize", "🗂️", "Sort-into-groups questions"),
    ("lab", "🧪", "The Function Lab"),
    ("debug", "🐞", "Debugging missions"),
    ("coding", "💻", "Coding challenges"),
    ("hints", "💡", "Hints and explanations"),
    ("xp", "🏆", "XP and badges"),
]

FEEDBACK_TOPIC = "built-in functions"
