"""List Methods: The Python Challenge · mission content.

Source of truth: the List Methods deck (37 slides). It opens with a recap of the function call stack and recursion
(multiply(n), the base case, RecursionError without one, the Daily Challenge sum_of_numbers with a wrong base case),
then the methods with the deck's own examples: append in a loop -> [1, 2, 3]; extend -> [1, 2, 3, 4, 5, 6];
insert(1, 4) -> [1, 4, 2, 3]; pop() -> [1, 2]; remove(3) on [1, 3, 2, 3] -> [1, 2, 3]; clear() -> [];
index(3) on [1, 3, 2, 3] -> 1; count(2) -> 1; sort(); sorted(list_a) leaves list_a as [1, 3, 2]
("sort modifies the list, sorted creates a new sorted list"), and the Code Walkthrough: the Nth Fibonacci number
(0, 1, 1, 2, 3, 5, 8...; the first two terms are 0 and 1; input 3 -> 2, input 9 -> 34, so N counts from f(0) = 0).

Story: Sneha runs the volunteer desk at her college tech fest. The volunteers are a list, in sign-up order.
Taught (and only this): append / extend / insert / pop() (no argument) / remove / clear / index / count / sort,
sorted() vs sort(), methods that change the list give back None, and the errors: remove() and index() of a missing
value raise ValueError, pop() on an empty list raises IndexError, insert() past the end adds at the end, count()
of a missing value is 0. Not used: dictionaries, comprehensions, lambda, key=, try/except, slicing, pop(index).

Every expected output is checked against real Python by tests/verify_lmethods.py.
"""

TEAM = '["Ravi", "Anu", "Kiran"]'

CONCEPTS = {
    "append": "append() adds one item at the end",
    "extend": "extend() adds every item of a list",
    "append_vs_extend": "append() nests, extend() spreads",
    "insert": "insert() at a position",
    "pop": "pop() removes and gives back the last item",
    "remove": "remove() deletes the first match",
    "clear": "clear() empties the list",
    "errors": "Missing values and empty lists",
    "index": "index() finds the first position",
    "count": "count() counts a value",
    "sort": "sort() sorts the list itself",
    "sort_sorted": "sort() vs sorted()",
    "returns_none": "Methods that give back None",
    "recap": "Recap: recursion and Fibonacci",
}

TYPE_LABEL = {
    "mcq": "Multiple choice", "msq": "Multiple select", "tf": "True or false",
    "ar": "Assertion and reasoning", "fill": "Fill in the blanks", "match": "Match the columns",
    "order": "Put in order", "categorize": "Sort into groups", "numeric": "Numeric answer",
    "predict": "Predict the output", "debug": "Debug mission", "coding": "Coding challenge",
}

ORDER = 3  # where this session sits in the course (session pickers list them in this order)
SLUG = "list-methods"  # this mission's URL: /list-methods/ (and /list-methods/teacher)
MISSION_MINUTES = 45  # the clock ends the mission here and the feedback opens (MISSION_MINUTES in the environment overrides it)

XP = {"mcq": 10, "tf": 10, "predict": 15, "msq": 15, "ar": 15, "fill": 15, "numeric": 15,
      "match": 20, "order": 20, "categorize": 20, "debug": 20, "coding": 40}
# Seconds per question, as in Session 30: questions with code get time for every line to trace:
# base + per line, never less than the floor. Coding gets 6 minutes.
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
    "list-builder": {"name": "List Builder", "desc": "Clear Sign-ups Open"},
    "list-cleaner": {"name": "List Cleaner", "desc": "Clear The Drop-outs"},
    "name-finder": {"name": "Name Finder", "desc": "Clear Find and Count"},
    "sort-master": {"name": "Sort Master", "desc": "Clear Sort It Out"},
    "bug-hunter": {"name": "Bug Hunter", "desc": "Clear Fix the Fest Apps"},
    "fest-champion": {"name": "List Methods Champion", "desc": "Run the fest desk"},
    "combo-5": {"name": "On Fire", "desc": "5 right answers in a row"},
    "clean-sweep": {"name": "Clean Sweep", "desc": "3 stars on any stage"},
    "bug-spotter": {"name": "Bug Spotter", "desc": "Every debug mission right on the first try"},
}
STAGE_BADGE = {"L1": "list-builder", "L2": "list-cleaner", "L3": "name-finder", "L4": "sort-master",
               "L5": "bug-hunter", "BOSS": "fest-champion"}
VISUAL_PRO = ("debug", "bug-spotter")

BOSS_SCENARIO = f'''team = {TEAM}
late = ["Sai", "Anu"]
team.extend(late)
team.insert(0, "Divya")
gone = team.pop()
team.remove("Ravi")
gate = sorted(team)
print(gone, team.count("Anu"))
print(team)
print(gate)'''

LEVELS = [
    {
        "id": "L0", "name": "The Volunteer Desk", "difficulty": "Warm-up",
        "job": "Meet Sneha's volunteer list. See how a list method changes the list it is called on.",
        "intel_title": "What you need to know",
        "intel": [
            "Sneha keeps the fest volunteers in one list, in the order they signed up: <code>team = [\"Ravi\", \"Anu\", \"Kiran\"]</code>.",
            "A <b>list method</b> is a job the list does on itself. Write the list, a dot, and the method: <code>team.append(\"Sai\")</code>.",
            "Most list methods <b>change the list itself</b>. No new list is made, so there is nothing to store.",
        ],
        "demo": f'team = {TEAM}\nteam.append("Sai")\nprint(team)\nprint(len(team))',
        "learn": ["Call a method on a list", "Say what append() does to the list"],
        "walk": [{"line": 1, "say": "Three volunteers, in sign-up order."},
                 {"line": 2, "say": "append() adds Sai at the end of the same list."},
                 {"line": 3, "say": "team itself has changed.", "shows": "['Ravi', 'Anu', 'Kiran', 'Sai']"},
                 {"line": 4, "say": "Four volunteers now.", "shows": "4"}],
        "main": ["L0-1", "L0-2"],
    },
    {
        "id": "L1", "name": "Sign-ups Open", "difficulty": "Easy",
        "job": "Volunteers are signing up: one at a time, a whole team at once, and one who must stand near the front. Add each of them the right way.",
        "intel_title": "What you need to know",
        "intel": [
            '<code>team.append(x)</code> adds one item at the end. Careful: <code>team.append(["Sai", "Meena"])</code> adds the whole list as <b>one</b> item.',
            "<code>team.extend(other)</code> adds <b>every</b> item of another list at the end: <code>[1, 2, 3]</code> extended with <code>[4, 5, 6]</code> is <code>[1, 2, 3, 4, 5, 6]</code>.",
            "<code>team.insert(1, x)</code> puts x at index 1 and moves the rest right: <code>[1, 2, 3]</code> becomes <code>[1, 4, 2, 3]</code> after <code>insert(1, 4)</code>.",
        ],
        "demo": 'list_a = []\nfor x in range(1, 4):\n    list_a.append(x)\nprint(list_a)\nlist_b = [4, 5, 6]\nlist_a.extend(list_b)\nprint(list_a)\nlist_c = [1, 2, 3]\nlist_c.insert(1, 4)\nprint(list_c)',
        "learn": ["Add one item with append()", "Add every item of a list with extend()", "Put an item at a position with insert()"],
        "walk": [{"line": 3, "say": "Each time round the loop, one number goes on the end."},
                 {"line": 4, "say": "Three appends, three items.", "shows": "[1, 2, 3]"},
                 {"line": 6, "say": "extend() adds 4, 5 and 6 as three separate items."},
                 {"line": 7, "say": "Six items, no list inside the list.", "shows": "[1, 2, 3, 4, 5, 6]"},
                 {"line": 9, "say": "insert(1, 4): 4 goes to index 1; 2 and 3 move one place right."},
                 {"line": 10, "say": "Nothing is replaced: the list grew by one.", "shows": "[1, 4, 2, 3]"}],
        "main": ["L1-1", "L1-2", "L1-3", "L1-4", "L1-5"],
    },
    {
        "id": "L2", "name": "The Drop-outs", "difficulty": "Easy+",
        "job": "Some volunteers drop out. Remove the right person each time: the last one in, a named one, or everyone once the fest is over. Don't crash the app.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>team.pop()</code> removes the last item and gives it back: <code>gone = team.pop()</code>. On an empty list it stops with IndexError.",
            '<code>team.remove("Anu")</code> removes the first "Anu" only. If the name is not in the list, it stops with ValueError.',
            "<code>team.clear()</code> removes every item: <code>[]</code>. The list itself is still there.",
        ],
        "demo": 'list_a = [1, 3, 2, 3]\nlist_a.remove(3)\nprint(list_a)\nlast = list_a.pop()\nprint(last, list_a)\nlist_a.clear()\nprint(list_a)',
        "learn": ["Remove the last item with pop() and keep it", "Remove the first match with remove()", "Empty a list with clear(), and spot the errors"],
        "walk": [{"line": 2, "say": "remove(3) takes out the first 3 only, at index 1."},
                 {"line": 3, "say": "The second 3 is still there.", "shows": "[1, 2, 3]"},
                 {"line": 4, "say": "pop() takes the last item, 3, and gives it to last."},
                 {"line": 5, "say": "last holds the removed item.", "shows": "3 [1, 2]"},
                 {"line": 6, "say": "clear() removes everything that is left."},
                 {"line": 7, "say": "An empty list, still named list_a.", "shows": "[]"}],
        "main": ["L2-1", "L2-2", "L2-4", "L2-5"],
    },
    {
        "id": "L3", "name": "Find and Count", "difficulty": "Medium",
        "job": "The gate asks two things all day: where is this volunteer in the queue, and how many shifts did each one take? Answer fast, and never crash on a name that is not there.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>queue.index(\"Ravi\")</code> gives the position of the <b>first</b> \"Ravi\", counting from 0. In <code>[1, 3, 2, 3]</code>, <code>index(3)</code> is <code>1</code>.",
            "Not in the list? <code>index()</code> stops with <b>ValueError</b>. Check with <code>in</code> first.",
            "<code>shifts.count(\"Ravi\")</code> counts how many times \"Ravi\" is in the list. A value that is not there gives <code>0</code>, no error.",
        ],
        "demo": 'shifts = ["Ravi", "Anu", "Ravi", "Kiran"]\nprint(shifts.index("Ravi"))\nprint(shifts.count("Ravi"))\nprint(shifts.count("Sai"))\nif "Sai" in shifts:\n    print(shifts.index("Sai"))\nelse:\n    print("Sai is not on the list")',
        "learn": ["Find the first position with index()", "Count a value with count()", "Avoid the ValueError of a missing value"],
        "walk": [{"line": 2, "say": "Ravi is at index 0 and index 2. index() gives the first.", "shows": "0"},
                 {"line": 3, "say": "Ravi took two shifts.", "shows": "2"},
                 {"line": 4, "say": "Sai took none: 0, and no error.", "shows": "0"},
                 {"line": 5, "say": "Check with in before you ask index()."},
                 {"line": 8, "say": "Sai is not there, so index() is never called.", "shows": "Sai is not on the list"}],
        "main": ["L3-1", "L3-2", "L3-3", "L3-4", "L3-5"],
    },
    {
        "id": "L4", "name": "Sort It Out", "difficulty": "Hard",
        "job": "The gate wants the list A to Z. But the first to sign up get the first T-shirts, so Sneha must keep the sign-up order too. Sort without losing it.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>team.sort()</code> sorts the list <b>itself</b>, smallest first (A to Z for names). The old order is gone.",
            "<code>sorted(team)</code> makes a <b>new</b> sorted list and leaves team as it was. <code>sorted(list_a)</code> alone, with nothing to keep it, changes nothing.",
            "Methods that change the list, like <code>sort()</code>, <code>append()</code> and <code>insert()</code>, give back <b>None</b>. So <code>print(team.sort())</code> prints <code>None</code>.",
        ],
        "demo": 'list_a = [1, 3, 2]\nsorted(list_a)\nprint(list_a)\nnew = sorted(list_a)\nprint(new, list_a)\nprint(list_a.sort())\nprint(list_a)',
        "learn": ["Sort a list with sort()", "Keep the old order with sorted()", "Know which methods give back None"],
        "walk": [{"line": 2, "say": "sorted() makes a new list, but nothing keeps it."},
                 {"line": 3, "say": "list_a is unchanged.", "shows": "[1, 3, 2]"},
                 {"line": 4, "say": "This time the new list gets a name."},
                 {"line": 5, "say": "Two lists: the sorted one and the old one.", "shows": "[1, 2, 3] [1, 3, 2]"},
                 {"line": 6, "say": "sort() sorts list_a and gives back None.", "shows": "None"},
                 {"line": 7, "say": "list_a itself is sorted now.", "shows": "[1, 2, 3]"}],
        "main": ["L4-1", "L4-2", "L4-3", "L4-4"],
    },
    {
        "id": "L5", "name": "Fix the Fest Apps", "difficulty": "Hard",
        "job": "The coding club's Fibonacci stall needs a better screen. Extend it so it works for every N, not just the examples.",
        "intel_title": "Before you start",
        "intel": [
            "Your code reads input and prints. Sample tests show the output; hidden tests try tricky cases, like N = 0 or N = 1.",
            "A recap from last class: recursion and its base case. Build the list of terms with <code>append()</code>.",
        ],
        "demo": 'team = []\nfor name in ["Ravi", "Anu"]:\n    team.append(name)\nprint(team)\nfib = [0, 1]\nfor i in range(2, 7):\n    fib.append(fib[i - 1] + fib[i - 2])\nprint(fib)',
        "learn": ["Fix a list that turns into None", "Build a list with append() in a loop", "Find a wrong base case"],
        "walk": [{"line": 3, "say": "Call append() on its own line. Don't store what it gives back."},
                 {"line": 4, "say": "Both names are kept, in order.", "shows": "['Ravi', 'Anu']"},
                 {"line": 5, "say": "The first two Fibonacci terms are 0 and 1."},
                 {"line": 7, "say": "Each new term is the sum of the two before it."},
                 {"line": 8, "say": "f(0) to f(6).", "shows": "[0, 1, 1, 2, 3, 5, 8]"}],
        "main": ["L5-3"],
    },
    {
        "id": "BOSS", "name": "Fest Day", "difficulty": "Boss",
        "job": "Fest day: late sign-ups, a guest at the front, drop-outs, and the gate wants its A to Z list. Run the desk.",
        "intel_title": "Before you start",
        "intel": [
            "Read the program on the left line by line. For each line, ask: does it change <code>team</code>, or make a new list?",
            "Last two jobs: tell an AI exactly what you want, then spot what its code gets wrong.",
        ],
        "demo": BOSS_SCENARIO,
        "learn": ["Trace many methods on one list", "Fix and rewrite a real program", "Write a spec an AI can follow"],
        "walk": [{"line": 3, "say": "extend() adds Sai and Anu as two items at the end."},
                 {"line": 4, "say": "Divya goes in at index 0, the front."},
                 {"line": 5, "say": "pop() takes the last item, the second Anu, and gives it to gone."},
                 {"line": 6, "say": "remove() takes Ravi out."},
                 {"line": 7, "say": "sorted() makes a new A to Z list for the gate. team keeps its order."},
                 {"line": 8, "say": "The popped Anu, and one Anu left in team.", "shows": "Anu 1"},
                 {"line": 9, "say": "team in its own order.", "shows": "['Divya', 'Anu', 'Kiran', 'Sai']"},
                 {"line": 10, "say": "The gate's A to Z list.", "shows": "['Anu', 'Divya', 'Kiran', 'Sai']"}],
        "main": ["B-1", "B-2", "B-3", "B-4"],
    },
]

# ---------------------------------------------------------------------------------------------
Q = []


def add(**q):
    q.setdefault("xp", XP[q["type"]])
    q.setdefault("time", timer(q))
    Q.append(q)


# ---------- L0 · The Volunteer Desk ----------
add(id="L0-1", stage="L0", type="mcq", level="Recall", concept="append",
    title='Ravi, Anu and Kiran have signed up. Then Sai walks up to the desk, and Sneha runs team.append("Sai"). Where does Sai go?',
    options=["At the end, after Kiran", "At the front, before Ravi", "Into a new list of his own", "Nowhere: append() only prints his name"],
    answer=0,
    why={1: "append() always adds at the <b>end</b>. Putting someone at the front needs <code>insert(0, ...)</code>.",
         2: "append() changes the same list. No new list is made.",
         3: "append() adds to the list. It prints nothing."},
    hints=["Think of a queue at the desk. Where does a new person stand?"],
    explain="<code>append()</code> adds one item at the <b>end</b> of the same list, so the sign-up order is kept: Ravi, Anu, Kiran, Sai.",
    trap="Thinking append() can put an item anywhere but the end.")

add(id="L0-2", stage="L0", type="tf", level="Recall", concept="append",
    title='True or false: team.append("Sai") changes team itself, so Sneha does not need to write team = ... to keep Sai.',
    value=True,
    hints=["Does append() change the list, or make a new one?"],
    explain="<code>append()</code> changes the list in place. After <code>team.append(\"Sai\")</code>, team already has Sai. Nothing needs to be stored.")

# ---------- L1 · Sign-ups Open ----------
add(id="L1-1", stage="L1", type="predict", level="Read", concept="append_vs_extend",
    title="Sai and Meena sign up together. What does this print?",
    code='team = ["Ravi", "Anu"]\nteam.append(["Sai", "Meena"])\nprint(team)\nprint(len(team))',
    options=["['Ravi', 'Anu', ['Sai', 'Meena']]\n3", "['Ravi', 'Anu', 'Sai', 'Meena']\n4",
             "['Ravi', 'Anu', ['Sai', 'Meena']]\n4", "!TypeError: list.append() takes exactly one argument (2 given)"],
    answer=0,
    why={1: "That is what <code>extend()</code> does. <code>append()</code> adds the whole list as <b>one</b> item.",
         2: "The inner list is one item, so <code>len()</code> counts it once: 3.",
         3: "Only one value is passed: a list. A list is allowed as an item."},
    hints=["append() always adds exactly one item. What is that one item here?", "len() counts the items of team, not what is inside them."],
    explain="<code>append()</code> adds its value as <b>one</b> item, so the list <code>['Sai', 'Meena']</code> sits inside team: 3 items. To add the two names separately, use <code>extend()</code>.",
    trap="Expecting append() to add Sai and Meena separately.")

add(id="L1-2", stage="L1", type="fill", level="Implement", concept="extend",
    title="The CSE team signs up together. Fill the gap so the program prints ['Ravi', 'Anu', 'Kiran', 'Sai', 'Meena'].",
    code=f'team = {TEAM}\ncse = ["Sai", "Meena"]\nteam.___(cse)\nprint(team)',
    blanks=[["extend"]],
    expect="['Ravi', 'Anu', 'Kiran', 'Sai', 'Meena']",
    hints=["Every item of cse must go in separately.", "append() would put the whole cse list in as one item."],
    explain="<code>team.extend(cse)</code> adds every item of cse at the end, one by one. <code>team.append(cse)</code> would add the list as one item: <code>['Ravi', 'Anu', 'Kiran', ['Sai', 'Meena']]</code>.",
    trap="Writing append, which nests the list.")

add(id="L1-3", stage="L1", type="mcq", level="Implement", concept="insert",
    title=f'team = {TEAM}. Divya is the chief guest\'s helper and must be second in the list. Which line does it, without losing anyone?',
    options=['team.insert(1, "Divya")', 'team.insert(2, "Divya")', 'team.insert("Divya", 1)', 'team[1] = "Divya"'],
    answer=0,
    why={1: "Index 2 is the <b>third</b> place. Indexes count from 0.",
         2: "insert() takes the index first, then the value. This stops with TypeError.",
         3: "That <b>replaces</b> Anu. Anu is lost."},
    hints=["Second place is index 1.", "insert(index, value): which comes first?"],
    explain="<code>team.insert(1, \"Divya\")</code> puts Divya at index 1, the second place, and moves Anu and Kiran one place right: <code>['Ravi', 'Divya', 'Anu', 'Kiran']</code>.",
    trap="Using team[1] = ..., which replaces instead of inserting.")

add(id="L1-4", stage="L1", type="tf", level="Read", concept="insert",
    title='True or false: team = ["Ravi", "Anu"]; team.insert(10, "Divya") stops with IndexError, because the list has no index 10.',
    value=False,
    hints=["Try it in your head: what can insert() do when the index is past the end?"],
    explain="No error. When the index is past the end, <code>insert()</code> adds the item at the <b>end</b>: <code>['Ravi', 'Anu', 'Divya']</code>.",
    trap="Expecting insert() to fail like team[10] does.")

add(id="L1-5", stage="L1", type="order", level="Implement", concept="insert",
    title="Put the lines in order so the program prints ['Ravi', 'Anu', 'Sai'], then Divya 4.",
    items=['print(team[0], len(team))', 'team.extend(["Anu", "Sai"])', 'team = ["Ravi"]', 'team.insert(0, "Divya")', 'print(team)'],
    mapping=[2, 1, 4, 3, 0],
    expect="['Ravi', 'Anu', 'Sai']\nDivya 4",
    hints=["The list has to exist before any method is called on it.", "Divya is not in the first print, but she is at index 0 in the second."],
    explain="Make the list, extend it with Anu and Sai, print the three names, then insert Divya at the front: now index 0 is Divya and there are 4 names.")

# ---------- L2 · The Drop-outs ----------
add(id="L2-1", stage="L2", type="predict", level="Read", concept="remove",
    title="Two students named Anu signed up. The first Anu drops out. What does this print?",
    code='team = ["Ravi", "Anu", "Kiran", "Anu"]\nteam.remove("Anu")\nprint(team)',
    options=["['Ravi', 'Kiran', 'Anu']", "['Ravi', 'Kiran']", "['Ravi', 'Anu', 'Kiran']", "!ValueError: list.remove(x): x not in list"],
    answer=0,
    why={1: "remove() takes out only <b>one</b> item: the first match.",
         2: "remove() starts looking from the front, so the first Anu goes, not the last.",
         3: "Anu is in the list, so there is no error."},
    hints=["How many items does one remove() take out?", "Which Anu does it find first?"],
    explain="<code>remove(\"Anu\")</code> deletes the <b>first</b> \"Anu\" only, at index 1. The second Anu stays.",
    trap="Thinking remove() deletes every match.")

add(id="L2-2", stage="L2", type="fill", level="Implement", concept="pop",
    title="The last volunteer to sign up leaves. Fill the gap so the program prints Bye Kiran, then ['Ravi', 'Anu'].",
    code=f'team = {TEAM}\ngone = team.___()\nprint("Bye", gone)\nprint(team)',
    blanks=[["pop"]],
    expect="Bye Kiran\n['Ravi', 'Anu']",
    hints=["Which method removes the last item?", "It must also give the removed name back, so gone can hold it."],
    explain="<code>team.pop()</code> removes the last item and gives it back, so <code>gone</code> is \"Kiran\". <code>clear()</code> or <code>remove()</code> give back None.",
    trap="Thinking pop() gives back None, like remove().")

add(id="L2-4", stage="L2", type="categorize", level="Read", concept="clear",
    title=f'Each line starts from team = {TEAM}. What does it do?',
    items=['team.pop()', 'team.remove("Anu")', 'team.clear()', 'team.remove("Sai")', 'team.clear(); team.pop()', 'team.remove("anu")'],
    categories=["Removes one item", "Removes every item", "Python stops with an error"],
    mapping=[0, 0, 1, 2, 2, 2],
    setup=f'team = {TEAM}',
    hints=["remove() needs an exact match, capital letters too.", "What can pop() take from an empty list?"],
    explain="<code>pop()</code> and <code>remove()</code> take out one item; <code>clear()</code> takes out all. <code>remove()</code> of a missing name (\"Sai\", or \"anu\" with a small a) stops with ValueError, and <code>pop()</code> on an empty list stops with IndexError.",
    trap="Forgetting that \"anu\" and \"Anu\" are different strings.")

add(id="L2-5", stage="L2", type="numeric", level="Read", concept="pop",
    title="Hours each volunteer worked. What number does this print?",
    code='hours = [3, 5, 2, 5, 4]\nhours.remove(5)\nlast = hours.pop()\nprint(last + len(hours))',
    value=7,
    hints=["remove(5) takes out the first 5 only.", "pop() gives back the last item, and the list gets shorter."],
    explain="After <code>remove(5)</code>: <code>[3, 2, 5, 4]</code>. <code>pop()</code> gives back 4 and leaves <code>[3, 2, 5]</code>, 3 items. 4 + 3 = 7.",
    trap="Removing both 5s, or forgetting that pop() shortens the list.")

# ---------- L3 · Find and Count ----------
add(id="L3-1", stage="L3", type="numeric", level="Read", concept="index",
    title="Ravi is in the T-shirt queue twice: he came back for a second size. What number does this print?",
    code='queue = ["Anu", "Ravi", "Kiran", "Ravi"]\nprint(queue.index("Ravi"))',
    value=1,
    hints=["index() gives the first position only.", "Positions count from 0."],
    explain="<code>index()</code> gives the position of the <b>first</b> \"Ravi\". Counting from 0, that is 1.",
    trap="Answering 3 (the last Ravi) or 2 (counting from 1).")

add(id="L3-2", stage="L3", type="predict", level="Read", concept="count",
    title="One name per shift taken. What does this print?",
    code='shifts = ["Ravi", "Anu", "Ravi", "Kiran", "Ravi"]\nprint(shifts.count("Ravi"))\nprint(shifts.count("Sai"))\nprint(shifts.count("ravi"))',
    options=["3\n0\n0", "3\n0\n3", "3\n!ValueError: 'Sai' is not in list", "3\n-1\n-1"],
    answer=0,
    why={1: "\"ravi\" with a small r is a different string from \"Ravi\".",
         2: "count() of a missing value gives 0. Only index() and remove() stop with ValueError.",
         3: "count() counts. A value that is not there is counted 0 times, not -1."},
    hints=["What is the count of something that is not there?", "Are \"Ravi\" and \"ravi\" the same string?"],
    explain="Ravi took 3 shifts. Sai took none, so <code>count()</code> gives 0 with no error. \"ravi\" never appears (small r), so 0 again.",
    trap="Expecting count() of a missing name to stop with an error.")

add(id="L3-3", stage="L3", type="debug", level="Debug", concept="errors",
    title="The gate asks for Sai's place in the queue. Tap the line where Python stops, then choose what goes wrong.",
    code='queue = ["Anu", "Ravi", "Kiran"]\nname = "Sai"\nplace = queue.index(name)\nprint(name, "is at", place)',
    errors=["ValueError: 'Sai' is not in list", "Nothing: it prints Sai is at -1", "Nothing: it prints Sai is at None", "IndexError: list index out of range"],
    line=3, error=0, focus=3,
    hints=["Is Sai in the queue?", "What does index() do when it cannot find the value?"],
    explain="Sai is not in the queue, so <code>queue.index(name)</code> on line 3 stops with <code>ValueError: 'Sai' is not in list</code>. Check with <code>if name in queue:</code> first.",
    trap="Expecting index() to give -1 or None for a missing value.")

add(id="L3-4", stage="L3", type="msq", level="Read", concept="index",
    title='queue = ["Anu", "Ravi", "Kiran", "Ravi"]. Which of these print 1?',
    options=['print(queue.index("Ravi"))', 'print(queue.count("Ravi"))', 'print(queue.count("Kiran"))',
             'print(queue.index("Anu"))', 'print(queue.count("Sai") + 1)', 'print(queue.index("Kiran"))'],
    answers=[0, 2, 4],
    hints=["index() gives a position from 0. count() gives how many.", "count() of a name that is not there is 0."],
    explain="The first Ravi is at index 1; Kiran appears once; Sai appears 0 times, plus 1 is 1. Ravi appears twice, Anu is at index 0, and Kiran is at index 2.",
    trap="Mixing up index() (where) and count() (how many).")

add(id="L3-5", stage="L3", type="ar", level="Read", concept="count",
    title="Read the assertion and the reason.",
    assertion='queue = ["Anu", "Ravi"]. queue.count("Sai") gives 0.',
    reason="count() stops with ValueError when the value is not in the list.",
    options=AR_OPTIONS, answer=2,
    why={0: "R is false: count() never stops with an error.",
         1: "R is false: a missing value is simply counted 0 times.",
         3: "A is true: Sai is not in the queue, so the count is 0."},
    hints=["What does count() give for a value that is not there?", "Which methods stop with ValueError for a missing value?"],
    explain="A is true: Sai is not in the list, so the count is 0. R is false: <code>count()</code> never raises for a missing value. It is <code>index()</code> and <code>remove()</code> that stop with ValueError.",
    trap="Mixing up count() with index().")

# ---------- L4 · Sort It Out ----------
add(id="L4-1", stage="L4", type="predict", level="Read", concept="sort_sorted",
    title="Sneha wants an A to Z list for the gate. What does this print?",
    code=f'team = {TEAM}\nsorted(team)\nprint(team)',
    options=["['Ravi', 'Anu', 'Kiran']", "['Anu', 'Kiran', 'Ravi']", "None", "['Ravi', 'Kiran', 'Anu']"],
    answer=0,
    why={1: "<code>sorted()</code> makes a <b>new</b> list. It never changes team, and here nothing keeps the new list.",
         2: "team is printed, and team is still a list of three names.",
         3: "Nothing here reverses the list."},
    hints=["Does sorted() change team, or make a new list?", "Where does line 2 keep its result?"],
    explain="<code>sorted(team)</code> makes a new sorted list, but nothing keeps it, and team is unchanged. Write <code>gate = sorted(team)</code> to keep it, or <code>team.sort()</code> to sort team itself.",
    trap="Thinking sorted(team) sorts team.")

add(id="L4-2", stage="L4", type="predict", level="Read", concept="sort",
    title="What does this print?",
    code='hours = [5, 2, 4]\nprint(hours.sort())\nprint(hours)',
    options=["None\n[2, 4, 5]", "[2, 4, 5]\n[2, 4, 5]", "[2, 4, 5]\n[5, 2, 4]", "None\n[5, 2, 4]"],
    answer=0,
    why={1: "<code>sort()</code> sorts the list but gives back <b>None</b>, so the first print shows None.",
         2: "<code>sort()</code> changes hours itself, and gives back None.",
         3: "The sort did happen: hours itself is sorted."},
    hints=["What does sort() give back?", "Did hours itself change?"],
    explain="<code>sort()</code> sorts <code>hours</code> itself and gives back <code>None</code>, so line 2 prints None. Line 3 shows the sorted list.",
    trap="Printing hours.sort() and expecting the sorted list.")

add(id="L4-3", stage="L4", type="match", level="Read", concept="sort_sorted",
    title="Match each expression to its value after this code runs.",
    code='hours = [5, 2, 4]\na = sorted(hours)\nb = hours.append(3)\nhours.sort()',
    left=["a", "b", "hours", "sorted(hours, reverse=True)", "hours.count(9)"],
    right=["None", "[5, 4, 3, 2]", "[2, 4, 5]", "0", "[2, 3, 4, 5]"],
    mapping=[2, 0, 4, 1, 3],
    setup='hours = [5, 2, 4]\na = sorted(hours)\nb = hours.append(3)\nhours.sort()',
    hints=["a was made before 3 was added.", "What does append() give back?"],
    explain="<code>a</code> is a new list made before 3 joined: <code>[2, 4, 5]</code>. <code>append()</code> gives back None, so b is None. hours got 3 and was sorted: <code>[2, 3, 4, 5]</code>; reversed that is <code>[5, 4, 3, 2]</code>. There is no 9: count is 0.")

add(id="L4-4", stage="L4", type="categorize", level="Read", concept="returns_none",
    title=f'Each line starts from team = {TEAM}. What does it store in x?',
    items=['x = team.append("Sai")', 'x = sorted(team)', 'x = team.pop()', 'x = team.count("Anu")', 'x = team.sort()', 'x = team.index("Kiran")'],
    categories=["None", "A new list", "A name (a string)", "A number"],
    mapping=[0, 1, 2, 3, 0, 3],
    setup=f'team = {TEAM}',
    hints=["Methods that change the list give back None.", "Which method gives back the item it removed?"],
    explain="<code>append()</code> and <code>sort()</code> change team and give back None. <code>sorted()</code> gives a new list. <code>pop()</code> gives back the name it removed. <code>count()</code> and <code>index()</code> give numbers.",
    trap="Storing x = team.append(...) or x = team.sort() and expecting a list.")

# ---------- L5 · Fix the Fest Apps ----------
add(id="L5-3", stage="L5", type="coding", level="Extend", concept="recap",
    challenge={
        "title": "The Fibonacci Stall",
        "statement": "The coding club's stall shows the Fibonacci series: f(0) = 0, f(1) = 1, and every next term is the sum of the two before it (0, 1, 1, 2, 3, 5, 8...). The starter prints f(N) with the recursive fib() from class. Extend it: first print the list of every term from f(0) to f(N), built with append(), then f(N) on the next line.",
        "input_fmt": "One line: a whole number N, from 0 to 20.",
        "output_fmt": "Two lines: the list [f(0), f(1), ..., f(N)], then f(N).",
        "starter": 'def fib(n):\n    if n == 0:\n        return 0\n    if n == 1:\n        return 1\n    return fib(n - 1) + fib(n - 2)\n\nn = int(input())\nprint(fib(n))\n',
        "tests": [
            {"stdin": "9", "expected": "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]\n34"},
            {"stdin": "3", "expected": "[0, 1, 1, 2]\n2"},
            {"stdin": "0", "expected": "[0]\n0", "hidden": True, "note": "N is 0: just the first term"},
            {"stdin": "1", "expected": "[0, 1]\n1", "hidden": True, "note": "N is 1: the first two terms"},
            {"stdin": "12", "expected": "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]\n144", "hidden": True, "note": "a longer series"},
        ],
    },
    rules=[{"require": r"\.append\s*\(", "msg": "Build the series list with append()."}],
    solution='def fib(n):\n    if n == 0:\n        return 0\n    if n == 1:\n        return 1\n    return fib(n - 1) + fib(n - 2)\n\nn = int(input())\nseries = []\nfor i in range(n + 1):\n    series.append(fib(i))\nprint(series)\nprint(fib(n))\n',
    hints=["Start with an empty list, and loop i from 0 to N: range(n + 1).", "series.append(fib(i)) adds one term each time round."],
    explain="An empty list and a loop over <code>range(n + 1)</code> add f(0) to f(N) with <code>append()</code>. Then print the list and f(N). <code>range(n)</code> would stop one term short.",
    trap="Looping over range(n), which leaves out f(N).")

# ---------- Final Boss · Fest Day ----------
# The scenario is also the question's code, so its timer gets time for all 10 lines (not just the 45 s floor).
add(id="B-1", stage="BOSS", type="predict", level="Read", concept="sort_sorted", scenario=True, code=BOSS_SCENARIO,
    title="Run the scenario on the left. What does it print?",
    options=["Anu 1\n['Divya', 'Anu', 'Kiran', 'Sai']\n['Anu', 'Divya', 'Kiran', 'Sai']",
             "Anu 1\n['Anu', 'Divya', 'Kiran', 'Sai']\n['Anu', 'Divya', 'Kiran', 'Sai']",
             "Divya 2\n['Anu', 'Kiran', 'Sai', 'Anu']\n['Anu', 'Anu', 'Kiran', 'Sai']",
             "['Sai', 'Anu'] 1\n['Divya', 'Anu', 'Kiran']\n['Anu', 'Divya', 'Kiran']"],
    answer=0,
    why={1: "<code>sorted(team)</code> makes a new list for the gate. team keeps its own order.",
         2: "<code>pop()</code> takes the <b>last</b> item, the second Anu, not the first item.",
         3: "<code>extend()</code> adds Sai and Anu as two items, so the last item is Anu, not a list."},
    hints=["Write team down after each line, 3 to 6.", "Does line 7 change team?"],
    explain="extend adds Sai and Anu; insert puts Divya first; pop takes the last Anu into gone; remove takes Ravi out. team is <code>['Divya', 'Anu', 'Kiran', 'Sai']</code> with one Anu, and <code>sorted()</code> gives the gate a new A to Z list.",
    trap="Thinking sorted(team) also sorts team.")

add(id="B-2", stage="BOSS", type="coding", level="Optimize", concept="count",
    challenge={
        "title": "The Shift Report",
        "statement": "The shift sheet has one name per shift taken. Print each volunteer once, A to Z, with how many shifts they took, then the sheet as it was. The starter sorts the sheet itself, so its last line is wrong, and it counts with a loop inside a loop. Fix it: count with <b>count()</b>, and keep the sheet in its order.",
        "input_fmt": "One line: the names, one per shift, separated by spaces (at least one).",
        "output_fmt": "One line per volunteer, A to Z: the name and the number of shifts. Then print(shifts), in the order the shifts were taken.",
        "starter": 'shifts = input().split()\nshifts.sort()\ndone = []\nfor name in shifts:\n    if name not in done:\n        done.append(name)\n        total = 0\n        for s in shifts:\n            if s == name:\n                total = total + 1\n        print(name, total)\nprint(shifts)\n',
        "tests": [
            {"stdin": "Ravi Anu Ravi Kiran Ravi", "expected": "Anu 1\nKiran 1\nRavi 3\n['Ravi', 'Anu', 'Ravi', 'Kiran', 'Ravi']"},
            {"stdin": "Meena Sai Meena", "expected": "Meena 2\nSai 1\n['Meena', 'Sai', 'Meena']"},
            {"stdin": "Anu", "expected": "Anu 1\n['Anu']", "hidden": True, "note": "only one shift"},
            {"stdin": "Sai Ravi Anu", "expected": "Anu 1\nRavi 1\nSai 1\n['Sai', 'Ravi', 'Anu']", "hidden": True, "note": "everyone took one shift"},
            {"stdin": "Kiran Kiran Kiran", "expected": "Kiran 3\n['Kiran', 'Kiran', 'Kiran']", "hidden": True, "note": "one volunteer took every shift"},
        ],
    },
    rules=[
        {"require": r"\.count\s*\(", "msg": "Count each name with count()."},
        {"forbid": r"\.sort\s*\(", "msg": "Keep the sheet in its order: sorted() makes a new list, sort() changes the sheet."},
        {"forbid": r"total\s*=\s*total\s*\+", "msg": "Remove the counting loop: count() does that job."},
    ],
    solution='shifts = input().split()\ndone = []\nfor name in sorted(shifts):\n    if name not in done:\n        done.append(name)\n        print(name, shifts.count(name))\nprint(shifts)\n',
    hints=["Loop over sorted(shifts): a new A to Z list, while shifts keeps its order.", "shifts.count(name) replaces the whole inner loop."],
    explain="<code>for name in sorted(shifts):</code> walks a new A to Z list and leaves the sheet as it was, so the last line is right. <code>shifts.count(name)</code> does the inner loop's job in one call.",
    trap="Sorting the sheet itself with sort(), which loses the order the shifts were taken.")

add(id="B-3", stage="BOSS", type="msq", level="Prompting", concept="append",
    title="You ask an AI for a function that adds a late volunteer to Sneha's list. Which lines must your spec include so its code is right?",
    options=["It takes the list and a name: add_volunteer(team, name).",
             "It adds the name at the end with append(), so the sign-up order is kept.",
             "If the name is already on the list, it does not add it again.",
             "Example: team = [\"Ravi\"]; add_volunteer(team, \"Anu\"); print(team) shows ['Ravi', 'Anu'].",
             "Make the code short and smart.",
             "Sort the list A to Z after each new name."],
    answers=[0, 1, 2, 3],
    hints=["A good spec gives the inputs, what it does, the edge case and an example to check.", "Which line would break the sign-up order?"],
    explain="The AI needs the inputs, where the name goes (the end, with append()), the edge case of a name already on the list, and a checkable example. \"Short and smart\" gives it nothing to check, and sorting after each name destroys the sign-up order.",
    trap="Leaving out the edge case: a name that is already on the list.")

add(id="B-4", stage="BOSS", type="debug", level="Prompting", concept="returns_none",
    title="An AI wrote this to print the gate list A to Z, then the sign-up list as it was. Python stops. Tap the line that must be changed, then choose what goes wrong.",
    code=f'team = {TEAM}\ngate = team.sort()\nfor name in gate:\n    print(name)\nprint(team)',
    errors=["TypeError: 'NoneType' object is not iterable", "Nothing: it prints Anu, Kiran, Ravi, then ['Ravi', 'Anu', 'Kiran']",
            "AttributeError: 'list' object has no attribute 'sort'", "IndexError: list index out of range"],
    line=2, error=0, focus=2,
    hints=["What does sort() give back?", "The loop is where Python stops, but which line put None in gate?"],
    explain="<code>team.sort()</code> gives back None, so gate is None and the loop on line 3 stops with <code>TypeError: 'NoneType' object is not iterable</code>. It also sorted team, losing the sign-up order. Change line 2 to <code>gate = sorted(team)</code>.",
    trap="Trusting the AI's gate = team.sort().")

QUESTIONS = {q["id"]: q for q in Q}
LEVEL_IDS = [lvl["id"] for lvl in LEVELS]
LEVEL_BY_ID = {lvl["id"]: lvl for lvl in LEVELS}
TOTAL = sum(len(lvl["main"]) for lvl in LEVELS)

GUIDE_HTML = """<h3>Add · list_a = [1, 2, 3]</h3>
    <div class="tscroll"><table><thead><tr><th>Code</th><th>What it does</th><th>list_a after</th></tr></thead><tbody>
      <tr><td><code>list_a.append(4)</code></td><td>adds <b>one</b> item at the end</td><td><code>[1, 2, 3, 4]</code></td></tr>
      <tr><td><code>list_a.append([4, 5])</code></td><td>the whole list goes in as <b>one</b> item</td><td><code>[1, 2, 3, [4, 5]]</code></td></tr>
      <tr><td><code>list_a.extend([4, 5])</code></td><td>adds <b>every</b> item at the end</td><td><code>[1, 2, 3, 4, 5]</code></td></tr>
      <tr><td><code>list_a.insert(1, 4)</code></td><td>puts 4 at index 1; the rest move right (past the end: at the end)</td><td><code>[1, 4, 2, 3]</code></td></tr></tbody></table></div>
    <h3>Remove</h3>
    <div class="tscroll"><table><thead><tr><th>Code</th><th>What it does</th><th>Gives back</th></tr></thead><tbody>
      <tr><td><code>list_a.pop()</code></td><td>removes the <b>last</b> item: <code>[1, 2]</code></td><td>the item: <code>3</code></td></tr>
      <tr><td><code>[1, 3, 2, 3].remove(3)</code></td><td>removes the <b>first</b> 3 only: <code>[1, 2, 3]</code></td><td>None</td></tr>
      <tr><td><code>list_a.clear()</code></td><td>removes every item: <code>[]</code></td><td>None</td></tr></tbody></table></div>
    <h3>Find, count, sort</h3>
    <div class="tscroll"><table><thead><tr><th>Code</th><th>Gives</th></tr></thead><tbody>
      <tr><td><code>[1, 3, 2, 3].index(3)</code></td><td><code>1</code>: the <b>first</b> position, from 0</td></tr>
      <tr><td><code>list_a.count(2)</code></td><td><code>1</code>: how many times. Missing value: <code>0</code></td></tr>
      <tr><td><code>list_a.sort()</code></td><td>sorts list_a <b>itself</b>, smallest first; gives back None</td></tr>
      <tr><td><code>sorted(list_a)</code></td><td>a <b>new</b> sorted list; list_a keeps its order</td></tr></tbody></table></div>
    <h3>Remember</h3>
    <ul><li>Methods that change the list (<code>append</code>, <code>extend</code>, <code>insert</code>, <code>remove</code>, <code>clear</code>, <code>sort</code>) give back <b>None</b>. Never write <code>team = team.append(x)</code>.</li>
      <li><code>remove()</code> or <code>index()</code> of a missing value stops with <b>ValueError</b>. Check with <code>in</code> first.</li>
      <li><code>pop()</code> on an empty list stops with <b>IndexError</b>.</li>
      <li>Need the old order too? <code>gate = sorted(team)</code>, not <code>team.sort()</code>.</li></ul>"""

LAB_STARTER = '''team = ["Ravi", "Anu", "Kiran"]
team.append("Sai")
team.insert(1, "Divya")
print(team)
gone = team.pop()
print(gone, team)
print(sorted(team), team)
print(team.index("Anu"), team.count("Anu"))
'''

UI = {
    "id": "lmethods",
    "title": "List Methods: The Python Challenge",
    "short": "List Methods",
    "hero_h1": "Mission: <em>Run the Fest Desk</em>",
    "hero_p": "Sneha runs the volunteer desk at her college tech fest. The volunteers are one Python list, in sign-up order, and the app keeps going wrong. Help her add, remove, find, count and sort them, one stage at a time.",
    "story": """<p><b>Sneha runs the volunteer desk at her college tech fest.</b> Every volunteer goes into one Python list, in the order they sign up. Now the app is a mess: a whole team went in as one name, the wrong Anu was removed, and the A to Z gate list wiped out the sign-up order.</p>
      <h3>Your 3 jobs</h3>
      <ol><li>📝 <b>Fill the list.</b> Add volunteers one by one, a whole team at once, and one near the front.</li>
        <li>🧹 <b>Handle the drop-outs.</b> Remove the right person each time, without crashing the app.</li>
        <li>🔤 <b>Sort it out.</b> Give the gate an A to Z list and keep the sign-up order safe.</li></ol>
      <p class="win">You win when every stage is cleared and fest day runs smoothly.</p>""",
    "lab": "py",
    "lab_name": "Method Lab",
    "lab_starter": LAB_STARTER,
    "lab_tips": [
        'Run it first. Which line printed <code>Sai</code>, and why is Sai gone from the list after it?',
        'Change <code>append("Sai")</code> to <code>append(["Sai", "Meena"])</code>, then try <code>extend</code>. What is different?',
        'Add <code>print(team.sort())</code>. What prints, and what does <code>team</code> look like after?',
        'Try <code>team.remove("Zoya")</code>. Read the error, then fix it with an <code>if "Zoya" in team:</code> check.',
        'Insert at index 50: <code>team.insert(50, "Om")</code>. Where does Om end up?',
    ],
    "boss_win": "Fest day sorted!",
    "champion": "List Methods Champion",
    "guide_title": "Field guide: list methods",
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
    ("sort", "🗂️", "Sort-into-groups and put-in-order questions"),
    ("lab", "🧪", "The Method Lab"),
    ("debug", "🐞", "Debugging missions"),
    ("coding", "💻", "Coding challenges"),
    ("hints", "💡", "Hints and explanations"),
    ("xp", "🏆", "XP and badges"),
]

FEEDBACK_TOPIC = "list methods"
