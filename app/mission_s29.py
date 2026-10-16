"""Dictionaries: The Python Challenge · mission content.

Source of truth: Session 29 deck (29_dictionaries_student_view.html), the canteen price board.
Board values from the deck: tea 12, coffee 15, samosa 15, puff 20, maggi 30. dosa is never on the board.

Only what the deck teaches: pairs, {} / dict(), unique keys (last value wins, first position kept),
menu[key], KeyError vs get() -> None, `in` checks keys, add / change in place, case-sensitive keys,
del + len, keys() / values() / items(), looping, live views vs list() copies, dict() from two-item
pairs, hashable keys, and dict vs list vs tuple vs set.
Not taught here: pop, update, setdefault, copy, comprehensions, nested dicts, get() with a default.

Every expected output below is checked against real Python by tests/verify_content.py.
Fields the client never receives before an attempt: answer, answers, value, blanks, mapping, line,
error, target, why, solution, hidden-test `expected`, rules.
"""

MENU = '{"tea": 12, "coffee": 15, "samosa": 15, "puff": 20, "maggi": 30}'

CONCEPTS = {
    "pairs": "Key-value pairs",
    "creation": "Creating a dictionary",
    "empty": "Empty {} and dict()",
    "unique_keys": "Unique keys",
    "access": "menu[key] takes a key",
    "keyerror_get": "KeyError vs get()",
    "membership": "in checks keys",
    "add_change": "Add or change a key",
    "case": "Keys are case-sensitive",
    "delete_len": "del and len()",
    "views_methods": "keys(), values(), items()",
    "looping": "Looping over a dictionary",
    "live_views": "Live views vs list() copies",
    "dict_from_pairs": "dict() from pairs",
    "hashable_keys": "Keys must be immutable",
    "compare_types": "Dict vs list, tuple, set",
}

TYPE_LABEL = {
    "mcq": "Multiple choice", "msq": "Multiple select", "tf": "True or false",
    "ar": "Assertion and reasoning", "fill": "Fill in the blanks", "match": "Match the columns",
    "order": "Put in order", "categorize": "Sort into groups", "numeric": "Numeric answer",
    "predict": "Predict the output", "debug": "Debug mission", "coding": "Coding challenge",
    "board": "Board build",
}

# XP and countdown (seconds) by type. A question may override either.
XP = {"mcq": 10, "tf": 10, "predict": 15, "msq": 15, "ar": 15, "fill": 15, "numeric": 15,
      "match": 20, "order": 20, "categorize": 20, "debug": 20, "board": 25, "coding": 40}
TIME = {"mcq": 30, "tf": 25, "predict": 45, "msq": 50, "ar": 45, "fill": 50, "numeric": 45,
        "match": 60, "order": 60, "categorize": 60, "debug": 60, "board": 75, "coding": 180}
MISSION_MINUTES = 40  # this mission's clock (MISSION_MINUTES in the environment still overrides it)

AR_OPTIONS = [
    "Both A and R are true, and R explains A",
    "Both A and R are true, but R does not explain A",
    "A is true, but R is false",
    "A is false, but R is true",
]

BADGES = {
    "board-explorer": {"name": "Board Explorer", "desc": "Clear Board Starter"},
    "duplicate-detective": {"name": "Duplicate Detective", "desc": "Clear Board Builder"},
    "key-keeper": {"name": "Key Keeper", "desc": "Clear Lookup Arena"},
    "logic-detective": {"name": "Logic Detective", "desc": "Clear Logic Lab"},
    "bug-hunter": {"name": "Bug Hunter", "desc": "Clear Code Breaker"},
    "python-dicts-champion": {"name": "Python Dictionaries Champion", "desc": "Defeat the Final Boss"},
    "combo-5": {"name": "On Fire", "desc": "5 right answers in a row"},
    "clean-sweep": {"name": "Clean Sweep", "desc": "3 stars on any stage"},
    "board-pro": {"name": "Board Pro", "desc": "Both Board builds right on the first try"},
    "bonus-star": {"name": "Bonus Star", "desc": "Clear the optional Bonus Round"},
}
STAGE_BADGE = {"L1": "board-explorer", "L2": "duplicate-detective", "L3": "key-keeper",
               "L4": "logic-detective", "L5": "bug-hunter", "BOSS": "python-dicts-champion", "BONUS": "bonus-star"}

BOSS_SCENARIO = '''menu = {"tea": 12, "coffee": 15, "samosa": 15}
updates = [("chai", 10), ("coffee", 18), ("samosa", 15), ("dosa", 20), ("chai", 12)]
for name, price in updates:
    menu[name] = price
print(menu)'''

LEVELS = [
    {
        "id": "L0", "name": "Mission Briefing", "difficulty": "Warm-up",
        "intel": [
            "A dictionary stores <b>pairs</b>: a <b>key</b> (the name tag) and its <b>value</b> (the price card). One pair is one item.",
            "Write it with curly brackets and colons: <code>{\"tea\": 12, \"coffee\": 15}</code>. Colons mean dictionary.",
            "You find a price by its <b>name</b>, never by counting rows.",
        ],
        "demo": 'menu = {"tea": 12, "coffee": 15, "samosa": 15, "puff": 20, "maggi": 30}\nprint(menu["maggi"])\nprint(type(menu))\nprint(len(menu))',
        "main": ["L0-1", "L0-2"],
    },
    {
        "id": "L1", "name": "Board Starter", "difficulty": "Easy",
        "intel": [
            "<code>{}</code> is an <b>empty dictionary</b>, not an empty set. <code>dict()</code> also makes one.",
            "<code>menu[\"samosa\"]</code> reads the value stored with the key <code>\"samosa\"</code>.",
            "<code>len(menu)</code> counts <b>pairs</b>, not keys plus values.",
        ],
        "demo": 'menu = {}\nprint(type(menu))\nmenu = {"tea": 12, "samosa": 15}\nprint(menu["samosa"])\nprint(len(menu))',
        "main": ["L1-1", "L1-2", "L1-3", "L1-4"],
    },
    {
        "id": "L2", "name": "Board Builder", "difficulty": "Easy+",
        "intel": [
            "Keys are <b>unique</b>. Write a key twice and there is no error: the <b>last value wins</b> and the key keeps its <b>first position</b>. Values can repeat.",
            "<code>menu[key] = value</code> is one line with two jobs: a <b>new</b> key adds a row at the end, an <b>existing</b> key changes its value in place.",
            "Keys are <b>case-sensitive</b>: <code>\"Tea\"</code> and <code>\"tea\"</code> are two different rows.",
            "<code>del menu[key]</code> removes the whole pair. A missing key raises <code>KeyError</code>.",
        ],
        "demo": 'menu = {"tea": 12, "coffee": 15, "tea": 14}\nprint(menu)\nmenu["bun"] = 10\nmenu["coffee"] = 18\nmenu["Tea"] = 16\ndel menu["bun"]\nprint(menu)\nprint(len(menu))',
        "main": ["L2-1", "L2-2", "L2-3", "L2-5", "L2-6", "L2-7"],
    },
    {
        "id": "L3", "name": "Lookup Arena", "difficulty": "Medium",
        "intel": [
            "A missing key with <code>[ ]</code> raises <code>KeyError</code> and the program <b>stops</b>. <code>get()</code> returns <code>None</code> and the program <b>continues</b>.",
            "<code>in</code> checks the <b>keys</b> only, never the values: <code>15 in menu</code> is <code>False</code>.",
            "<code>keys()</code>, <code>values()</code> and <code>items()</code> follow the order the pairs were added. <code>values()</code> keeps repeats.",
            "<code>for name in menu:</code> gives the keys. <code>for name, price in menu.items():</code> gives both.",
        ],
        "demo": 'menu = {"tea": 12, "coffee": 15, "samosa": 15}\nprint(menu.get("dosa"))\nprint("dosa" in menu, 15 in menu)\nprint(list(menu.values()))\nfor name, price in menu.items():\n    print(name, price)',
        "main": ["L3-1", "L3-3", "L3-4", "L3-6", "L3-7", "L3-8"],
    },
    {
        "id": "L4", "name": "Logic Lab", "difficulty": "Hard",
        "intel": [
            "<code>menu.keys()</code> is a <b>live view</b>: it shows every later change. <code>list(menu.keys())</code> is a <b>fixed copy</b> taken at that moment.",
            "<code>dict(pairs)</code> builds a board from a list of <b>two-item</b> pairs. A flat list, or an element with three items, raises <code>ValueError</code>.",
            "Keys must be <b>immutable</b>: a tuple works, a list raises <code>TypeError: unhashable type: 'list'</code>. Values can be anything.",
            "Dictionaries keep <b>insertion order</b>. Deleting a key and adding it again puts it at the end.",
        ],
        "demo": 'menu = {"tea": 12, "coffee": 15}\nview = menu.keys()\nphoto = list(menu.keys())\nmenu["samosa"] = 15\nprint(view)\nprint(photo)\nprint(dict([("tea", 12), ("bun", 10)]))',
        "main": ["L4-1", "L4-3", "L4-4", "L4-5", "L4-6", "L4-7"],
    },
    {
        "id": "L5", "name": "Code Breaker", "difficulty": "Hard",
        "intel": [
            "Each challenge reads input, uses a dictionary and prints. Sample tests show the format; <b>hidden tests</b> check the edge cases.",
            "Guard a lookup with <code>if item in menu:</code> so a missing item is skipped instead of crashing.",
            "Output is checked <b>exactly</b>. Dictionaries keep insertion order, so the order you print in matters.",
        ],
        "demo": f'menu = {MENU}\norder = "tea dosa samosa".split()\ntotal = 0\nfor item in order:\n    if item in menu:\n        total = total + menu[item]\nprint(total)',
        "main": ["L5-1", "L5-2"],
    },
    {
        "id": "BOSS", "name": "Final Boss", "difficulty": "Boss",
        "intel": [
            "One canteen scenario mixes everything: adding, changing, repeated keys, <code>dict()</code>, a fix, a rewrite and an AI that needs a clear spec.",
            "Trace the scenario below line by line before you answer. The board keeps insertion order.",
            "An AI writes what you ask for. A vague spec gets plausible code that may break the board.",
        ],
        "demo": BOSS_SCENARIO,
        "main": ["B-1", "B-4", "B-5", "B-6"],
    },
    {
        "id": "BONUS", "name": "Bonus Round", "difficulty": "Optional", "bonus": True,
        "intel": [
            "Your mission is already <b>complete</b>. This round is extra: five quick questions for more XP and the <b>Bonus Star</b> badge.",
            "Each one mixes two ideas from today. Read the code slowly.",
            "You can stop any time: press <b>Finish</b> on the map to see your report.",
        ],
        "demo": 'menu = {"tea": 12}\nmenu["chai"] = menu["tea"]\nprint(menu)',
        "main": ["X-1", "X-2", "X-3", "X-4", "X-5"],
    },
]

# ---------------------------------------------------------------------------------------------
Q = []


def add(**q):
    q.setdefault("xp", XP[q["type"]])
    q.setdefault("time", TIME[q["type"]])
    Q.append(q)


# ---------- L0 · Mission Briefing ----------
add(id="L0-1", stage="L0", type="mcq", level="Recall", concept="pairs",
    title='On the canteen board, menu = {"tea": 12}. Which part is the key?',
    options=['"tea"', "12", "The colon :", "The whole board"],
    answer=0,
    why={1: "12 is the <b>value</b>: the price card. The key is the name tag you look it up by.",
         2: "The colon only separates the key from its value.",
         3: "The board is the whole dictionary. Each row on it is one key-value pair."},
    hints=["Think of the board: a name tag on the left, a price card on the right. Which one do you search for?"],
    explain='<code>"tea"</code> is the key (the name tag) and <code>12</code> is its value (the price card). Together they make one pair.',
    trap="The value is what you want to read, but you always find it by its key.")

add(id="L0-2", stage="L0", type="tf", level="Recall", concept="creation",
    title='True or false: print(type({"tea": 12})) prints <class \'dict\'>.',
    value=True,
    hints=["Curly brackets with colons inside build one kind of collection. Which one?"],
    explain='Curly brackets with <code>key: value</code> pairs build a dictionary, so <code>type()</code> reports <code>&lt;class \'dict\'&gt;</code>.',
    trap="Curly brackets alone do not mean set. The colons make it a dictionary.")

# ---------- L1 · Board Starter ----------
add(id="L1-1", stage="L1", type="predict", level="Read", concept="empty",
    title="What does this print?",
    code="menu = {}\nprint(type(menu))",
    options=["<class 'dict'>", "<class 'set'>", "<class 'list'>", "!SyntaxError: invalid syntax"],
    answer=0,
    why={1: "<code>{}</code> is an empty <b>dictionary</b>. An empty set needs <code>set()</code>.",
         2: "A list uses square brackets <code>[]</code>.",
         3: "<code>{}</code> is valid Python. It is the most common way to start an empty board."},
    hints=["Empty curly brackets were a dictionary long before sets existed in Python."],
    explain="<code>{}</code> makes an empty dictionary. <code>dict()</code> does the same.",
    trap="Many expect an empty set. Empty curly brackets always mean an empty dict.")

add(id="L1-2", stage="L1", type="categorize", level="Recall", concept="creation",
    title="Which of these make a dictionary?",
    items=['{}', '{"tea": 12}', '{"tea", "coffee"}', 'dict()', 'set()', '["tea", 12]'],
    categories=["dict", "not a dict"],
    mapping=[0, 0, 1, 0, 1, 1],
    hints=["Look for colons. Curly brackets without colons make a set, unless they are empty."],
    explain='<code>{}</code>, <code>{"tea": 12}</code> and <code>dict()</code> are dictionaries. <code>{"tea", "coffee"}</code> and <code>set()</code> are sets, and <code>["tea", 12]</code> is a list.',
    trap="<code>{\"tea\", \"coffee\"}</code> has curly brackets but no colons, so it is a set.")

add(id="L1-3", stage="L1", type="predict", level="Read", concept="access",
    title="What does this print?",
    code='menu = {"tea": 12, "samosa": 15}\nprint(menu["samosa"])',
    options=["15", "12", "!KeyError: 'samosa'", "samosa"],
    answer=0,
    why={1: "12 is stored with <code>\"tea\"</code>. The brackets hold the key <code>\"samosa\"</code>.",
         2: "<code>\"samosa\"</code> is on the board, so there is no error.",
         3: "<code>menu[key]</code> gives the <b>value</b>, not the key."},
    hints=["Find the name tag inside the brackets, then read the price next to it."],
    explain='<code>menu["samosa"]</code> finds the key <code>"samosa"</code> and gives its value, 15.')

add(id="L1-4", stage="L1", type="match", level="Read", concept="access",
    title='menu = {"tea": 12, "coffee": 15}. Match each expression to what it gives.',
    left=['menu["tea"]', "len(menu)", '"tea" in menu', "type(menu)"],
    right=["True", "<class 'dict'>", "12", "2"],
    mapping=[2, 3, 0, 1],
    hints=["len counts pairs. in asks a yes/no question about the keys."],
    explain='<code>menu["tea"]</code> gives 12, <code>len(menu)</code> counts 2 pairs, <code>"tea" in menu</code> is True and <code>type(menu)</code> is <code>&lt;class \'dict\'&gt;</code>.')

# ---------- L2 · Board Builder ----------
add(id="L2-1", stage="L2", type="predict", level="Read", concept="unique_keys",
    title="What does this print?",
    code='menu = {"tea": 12, "coffee": 15, "tea": 14}\nprint(menu)',
    options=["{'tea': 12, 'coffee': 15, 'tea': 14}", "{'tea': 14, 'coffee': 15}",
             "{'coffee': 15, 'tea': 14}", "{'tea': 12, 'coffee': 15}"],
    answer=1,
    why={0: "Keys are unique. A board cannot hold two <code>'tea'</code> rows.",
         2: "The repeated key keeps its <b>first</b> position. Only its value changes.",
         3: "Python reads left to right, so the <b>last</b> value for a key wins."},
    hints=["A key cannot appear twice. Which value survives, and where does the key stay?"],
    explain="No error. The repeated key keeps its first position and the last value wins: <code>{'tea': 14, 'coffee': 15}</code>.",
    trap="Expecting an error, or expecting tea to move to the end. Neither happens.")

add(id="L2-2", stage="L2", type="board", level="Implement", concept="add_change",
    title="Update the board.",
    start=[["tea", 12], ["coffee", 15]],
    goal="Tea's price goes up to <b>14</b>, and <b>samosa</b> arrives at <b>15</b>.",
    target=[["tea", 14], ["coffee", 15], ["samosa", 15]],
    hints=["Changing tea's price is the same line as adding a row: menu[key] = value. Where does each one end up?"],
    explain='<code>menu["tea"] = 14</code> changes tea in place. <code>menu["samosa"] = 15</code> is a new key, so it adds a row at the end: <code>{\'tea\': 14, \'coffee\': 15, \'samosa\': 15}</code>.',
    trap="Deleting tea and adding it again would move it to the end.")

add(id="L2-3", stage="L2", type="predict", level="Read", concept="case",
    title="What does this print?",
    code='menu = {"tea": 12, "samosa": 15}\nmenu["Tea"] = 16\nprint(len(menu))',
    options=["2", "3", "!KeyError: 'Tea'", "16"],
    answer=1,
    why={0: '<code>"Tea"</code> and <code>"tea"</code> are different strings, so this is a new key, not a change.',
         2: "Assigning to a missing key never raises an error. It adds the key.",
         3: "<code>len()</code> counts pairs. It does not show a price."},
    hints=["Is a capital T the same letter as a small t to Python?"],
    explain='Keys are case-sensitive. <code>"Tea"</code> is a new key, so the board has 3 rows.',
    trap='Thinking <code>menu["Tea"] = 16</code> updates tea.')

add(id="L2-5", stage="L2", type="msq", level="Read", concept="delete_len",
    title='menu = {"tea": 12, "puff": 20, "maggi": 30}, then del menu["puff"]. Which are now true?',
    options=["len(menu) is 2", '"puff" in menu is False', 'menu.get("puff") gives None',
             'menu["puff"] gives 0', "20 in menu.values() is True"],
    answers=[0, 1, 2],
    hints=["del wipes the whole row: the name tag and its price card."],
    explain='After <code>del</code> the puff pair is gone: 2 rows remain, <code>"puff" in menu</code> is False, and <code>get</code> gives None. <code>menu["puff"]</code> would raise <code>KeyError</code>, and 20 left with puff.',
    trap="Thinking a deleted key reads as 0. It is gone; [ ] raises KeyError.")

add(id="L2-6", stage="L2", type="board", level="Implement", concept="delete_len",
    title="Today's changes.",
    start=[["tea", 12], ["puff", 20], ["maggi", 30]],
    goal="Puff is <b>sold out</b>, maggi drops to <b>25</b>, and <b>coffee</b> arrives at <b>15</b>.",
    target=[["tea", 12], ["maggi", 25], ["coffee", 15]],
    hints=["Three different lines: del for sold out, menu[key] = value for the rest.", "A changed key stays where it is. A new key goes to the end."],
    explain='<code>del menu["puff"]</code>, then <code>menu["maggi"] = 25</code> (in place) and <code>menu["coffee"] = 15</code> (new, at the end): <code>{\'tea\': 12, \'maggi\': 25, \'coffee\': 15}</code>.',
    trap="Setting puff to 0 keeps the row. Sold out means the row is deleted.")

add(id="L2-7", stage="L2", type="order", level="Implement", concept="add_change",
    title="Put the lines in order so the program prints 1, then {'coffee': 15, 'tea': 14}.",
    items=['menu["tea"] = 14', 'print(menu)', 'menu = {"tea": 12, "coffee": 15}', 'print(len(menu))', 'del menu["tea"]'],
    mapping=[2, 4, 3, 0, 1],
    hints=["len is 1 only while tea is gone.", "A key that is deleted and added again goes to the end."],
    explain='Build the board, delete tea (1 row left), print the length, then add tea back. It is a new key now, so it goes to the end: <code>{\'coffee\': 15, \'tea\': 14}</code>.')

# ---------- L3 · Lookup Arena ----------
add(id="L3-1", stage="L3", type="predict", level="Read", concept="keyerror_get",
    title="What does this print?",
    code=f'menu = {MENU}\nprint(menu["dosa"])',
    options=["None", "0", "!KeyError: 'dosa'", "dosa"],
    answer=2,
    why={0: "<code>None</code> is what <code>get()</code> gives. Square brackets raise an error instead.",
         1: "Python never invents a price of 0 for a missing key.",
         3: "Square brackets return a value, never the key you typed."},
    hints=["dosa is not on the board. What do square brackets do when the key is missing?"],
    explain="<code>[ ]</code> with a missing key raises <code>KeyError: 'dosa'</code> and the program stops.",
    trap="Mixing up <code>[ ]</code> (error) with <code>get()</code> (None).")

add(id="L3-3", stage="L3", type="predict", level="Read", concept="membership",
    title="What does this print?",
    code='menu = {"tea": 12, "samosa": 15}\nprint(15 in menu)',
    options=["True", "False", "!KeyError: 15", "15"],
    answer=1,
    why={0: "15 is a <b>value</b>. <code>in</code> looks at the keys only.",
         2: "<code>in</code> never raises KeyError. It answers True or False.",
         3: "<code>in</code> gives True or False, never the item."},
    hints=["in reads the left column of the board only: the names."],
    explain="<code>in</code> checks the keys. The keys are tea and samosa, so <code>15 in menu</code> is False.",
    trap="Thinking <code>in</code> also searches the prices.")

add(id="L3-4", stage="L3", type="ar", level="Read", concept="access",
    title="Read the assertion and the reason.",
    assertion='menu = {"tea": 12, "coffee": 15, "samosa": 15}. print(menu[2]) raises KeyError: 2.',
    reason="Square brackets on a dictionary hold a key, never a position, and 2 is not a key on this board.",
    options=AR_OPTIONS, answer=0,
    why={1: "R is exactly why A happens: the 2 is treated as a key.",
         2: "R is true: brackets take a key, never a row number.",
         3: "A is true. Python looks for a key named 2 and does not find one."},
    hints=["Would menu[2] give the third row, like a list?"],
    explain="Both are true and R explains A. There is no row number in a dictionary, so <code>menu[2]</code> looks for a key named 2 and raises <code>KeyError: 2</code>.",
    trap="Treating a dictionary like a list and expecting the third price.")

add(id="L3-6", stage="L3", type="match", level="Read", concept="views_methods",
    title='menu = {"coffee": 15, "samosa": 15}. Match each expression to its result.',
    left=["list(menu.keys())", "list(menu.values())", "list(menu.items())", "len(menu)"],
    right=["2", "[('coffee', 15), ('samosa', 15)]", "['coffee', 'samosa']", "[15, 15]"],
    mapping=[2, 3, 1, 0],
    hints=["values() keeps repeats. items() gives (key, value) pairs."],
    explain="<code>keys()</code> gives the names, <code>values()</code> the prices (repeats kept: <code>[15, 15]</code>), <code>items()</code> the pairs, and <code>len</code> counts 2 pairs.",
    trap="Expecting <code>values()</code> to drop the repeated 15, like a set.")

add(id="L3-7", stage="L3", type="debug", level="Debug", concept="keyerror_get",
    title="Ravi's bill crashes. Tap the line that must be fixed, then choose what goes wrong.",
    code=f'menu = {MENU}\norder = ["tea", "dosa"]\ntotal = 0\nfor item in order:\n    total = total + menu[item]\nprint(total)',
    errors=["KeyError: 'dosa'", "TypeError", "It prints 12", "IndexError"],
    line=5, error=0, focus=5,
    hints=["Which item in the order is not on the board, and which line looks it up?"],
    explain="Line 5 reads <code>menu[item]</code> with <code>item = \"dosa\"</code>, which is not a key, so Python raises <code>KeyError: 'dosa'</code>. Guard it with <code>if item in menu:</code>.",
    trap="Blaming line 2. A list may hold any names; the crash is the lookup.")

add(id="L3-8", stage="L3", type="fill", level="Implement", concept="views_methods",
    title="Fill the gaps so the program prints every item that costs 15 or less: tea, coffee, samosa.",
    code=f'menu = {MENU}\nfor name, price in menu.___():\n    if price ___ 15:\n        print(name)',
    blanks=[["items"], ["<="]],
    hints=["Two loop variables need pairs. Which method gives (key, value) pairs?", "15 itself must be included."],
    explain="<code>menu.items()</code> gives each (name, price) pair, and <code>price &lt;= 15</code> keeps 12, 15 and 15.",
    trap="<code>&lt; 15</code> would leave out coffee and samosa.")

# ---------- L4 · Logic Lab ----------
add(id="L4-1", stage="L4", type="predict", level="Read", concept="live_views",
    title="What does this print?",
    code='menu = {"tea": 12, "coffee": 15}\nview = menu.keys()\nphoto = list(menu.keys())\nmenu["samosa"] = 15\nprint(len(view), len(photo))',
    options=["3 2", "2 2", "3 3", "2 3"],
    answer=0,
    why={1: "<code>view</code> is live: it sees samosa arrive.",
         2: "<code>photo</code> is a list copy taken before samosa arrived.",
         3: "The other way round: the view updates, the copy does not."},
    hints=["One of them is a window onto the board, the other is a photograph of it."],
    explain="<code>menu.keys()</code> is a live view, so it shows 3 keys. <code>list(...)</code> took a fixed copy with 2 keys.",
    trap="Thinking the view is frozen at the moment it was made.")

add(id="L4-3", stage="L4", type="categorize", level="Read", concept="dict_from_pairs",
    title="What happens when each line runs?",
    items=['dict([("tea", 12), ("coffee", 15)])', 'dict(["tea", 12, "coffee", 15])', 'dict([["tea", 12], ["bun", 10]])',
           'dict([("tea", 12, "hot")])', '{("tea", "samosa"): 27}', '{["tea", "samosa"]: 27}'],
    categories=["Works", "ValueError", "TypeError"],
    mapping=[0, 1, 0, 1, 0, 2],
    hints=["dict() needs every element to be exactly two items.", "A key must be immutable: tuples yes, lists no."],
    explain="Two-item pairs work, whether tuples or lists. A flat list or a three-item element raises <code>ValueError</code>. A tuple can be a key; a list key raises <code>TypeError: unhashable type: 'list'</code>.",
    trap="A flat list looks like pairs to us, but dict() sees single items.")

add(id="L4-4", stage="L4", type="debug", level="Debug", concept="hashable_keys",
    title="Teja wants a combo price on the board. Tap the line that must be fixed, then choose what goes wrong.",
    code='menu = {"tea": 12, "samosa": 15}\ncombo = menu["tea"] + menu["samosa"]\nmenu[["tea", "samosa"]] = combo\nprint(menu)',
    errors=["KeyError: 'tea'", "TypeError: unhashable type: 'list'", "ValueError", "Nothing goes wrong: it prints the combo"],
    line=3, error=1, focus=3,
    hints=["Keys must never change. Can a list change?"],
    explain='Line 3 uses a list as a key. Lists can change, so they cannot be keys: <code>TypeError: unhashable type: \'list\'</code>. A tuple works: <code>menu[("tea", "samosa")] = combo</code>.',
    trap="Line 2 is fine: both keys exist.")

add(id="L4-5", stage="L4", type="numeric", level="Read", concept="add_change",
    title="Trace the board. What number does this print?",
    code='menu = {"tea": 12, "coffee": 15}\nmenu["samosa"] = 15\nmenu["tea"] = 14\ndel menu["coffee"]\nmenu["Tea"] = 16\ntotal = 0\nfor price in menu.values():\n    total = total + price\nprint(total)',
    value=45,
    hints=["Write the board down after every line.", "Tea and tea are different keys."],
    explain="After the changes the board is <code>{'tea': 14, 'samosa': 15, 'Tea': 16}</code>. 14 + 15 + 16 = 45.",
    trap="Treating <code>\"Tea\"</code> as an update to tea gives 29.")

add(id="L4-6", stage="L4", type="msq", level="Read", concept="compare_types",
    title="Which are true for a dictionary, but not for a list?",
    options=["You find a value by its key, not by its position.", "Keys cannot repeat; values can.",
             "It has no order, so print shows the items in a random order.", "menu[0] gives the first item.",
             "Its items are key-value pairs."],
    answers=[0, 1, 4],
    hints=["Remember the canteen board: name tags and price cards, written in the order they arrived."],
    explain="A dictionary is looked up by key, its keys are unique, and each item is a pair. It <b>does</b> keep insertion order, and <code>menu[0]</code> looks for a key named 0.",
    trap="Saying dictionaries are unordered. They keep the order pairs were added.")

add(id="L4-7", stage="L4", type="predict", level="Read", concept="looping",
    title="What does this print?",
    code='menu = {"tea": 12, "coffee": 15, "samosa": 15}\ndel menu["tea"]\nmenu["tea"] = 13\nmenu["coffee"] = 16\nfor name in menu:\n    print(name, menu[name])',
    options=["tea 13\ncoffee 16\nsamosa 15", "coffee 16\nsamosa 15\ntea 13",
             "samosa 15\ntea 13\ncoffee 16", "coffee 15\nsamosa 15\ntea 13"],
    answer=1,
    why={0: "tea was deleted, so when it comes back it is a <b>new</b> key and goes to the end.",
         2: "Changing coffee's price keeps it in place. Only new keys go to the end.",
         3: "coffee's value was changed to 16 before the loop."},
    hints=["Deleted then added again: new key. Changed: same place."],
    explain="Deleting tea and adding it back puts tea at the end. Changing coffee keeps its place. Order: coffee 16, samosa 15, tea 13.",
    trap="Expecting tea to return to its old first position.")

# ---------- L5 · Code Breaker ----------
add(id="L5-1", stage="L5", type="coding", level="Implement", concept="membership",
    challenge={
        "title": "Canteen Bill",
        "statement": "Ravi hands in an order. Total the bill using the board. Items that are <b>not on the board</b> (like dosa) are skipped: they cost nothing and must not crash the program.",
        "input_fmt": "One line of item names separated by spaces. It may be empty.",
        "output_fmt": "One number: the total.",
        "starter": f'menu = {MENU}\norder = input().split()\ntotal = 0\n# add up the price of every item that is on the board\n\nprint(total)\n',
        "tests": [
            {"stdin": "puff tea tea coffee", "expected": "59"},
            {"stdin": "tea dosa samosa", "expected": "27"},
            {"stdin": "dosa burger", "expected": "0", "hidden": True, "note": "nothing on the board"},
            {"stdin": "Tea tea", "expected": "12", "hidden": True, "note": "Tea with a capital T"},
            {"stdin": "", "expected": "0", "hidden": True, "note": "empty order"},
        ],
    },
    solution=f'menu = {MENU}\norder = input().split()\ntotal = 0\nfor item in order:\n    if item in menu:\n        total = total + menu[item]\nprint(total)\n',
    hints=["Loop over the order and add menu[item] to total.", "Put if item in menu: in front of the lookup so missing items are skipped."],
    explain="Loop over the order, check <code>if item in menu:</code>, and add <code>menu[item]</code>. Tea is counted twice in the first sample because it was ordered twice.",
    trap="<code>\"Tea\"</code> is not a key, so it is skipped.")

add(id="L5-2", stage="L5", type="coding", level="Extend", concept="looping",
    challenge={
        "title": "Exam-Week Budget",
        "statement": "Exam week: how much can you buy? Read your budget. Print the <b>name</b> of every item that costs your budget or less, in board order, then print <b>how many</b> there were.",
        "input_fmt": "One whole number: the budget.",
        "output_fmt": "Each affordable name on its own line, then the count on the last line.",
        "starter": f'menu = {MENU}\nbudget = int(input())\ncount = 0\nfor price in menu.values():\n    if price <= budget:\n        count = count + 1\nprint(count)\n',
        "tests": [
            {"stdin": "15", "expected": "tea\ncoffee\nsamosa\n3"},
            {"stdin": "30", "expected": "tea\ncoffee\nsamosa\npuff\nmaggi\n5"},
            {"stdin": "10", "expected": "0", "hidden": True, "note": "too small for anything"},
            {"stdin": "12", "expected": "tea\n1", "hidden": True, "note": "price equal to the budget"},
            {"stdin": "0", "expected": "0", "hidden": True, "note": "no money"},
        ],
    },
    solution=f'menu = {MENU}\nbudget = int(input())\ncount = 0\nfor name, price in menu.items():\n    if price <= budget:\n        count = count + 1\n        print(name)\nprint(count)\n',
    hints=["The starter counts with values(). To print names too, loop with items().", "Print the name inside the if, and the count after the loop."],
    explain="Switch the loop to <code>for name, price in menu.items():</code> and print the name inside the <code>if</code>. The count prints once, after the loop.",
    trap="<code>&lt; budget</code> misses an item whose price equals the budget.")

# ---------- Final Boss ----------
add(id="B-1", stage="BOSS", type="predict", level="Read", concept="unique_keys", scenario=True,
    title="Run the scenario on the left. What does print(menu) show?",
    options=["{'tea': 12, 'coffee': 18, 'samosa': 15, 'chai': 12, 'dosa': 20}",
             "{'tea': 12, 'coffee': 18, 'samosa': 15, 'chai': 10, 'dosa': 20}",
             "{'tea': 12, 'coffee': 18, 'samosa': 15, 'dosa': 20, 'chai': 12}",
             "!KeyError: 'chai'"],
    answer=0,
    why={1: "chai is updated twice. The last value, 12, wins.",
         2: "The second chai is a change, not a new key, so chai keeps its first position.",
         3: "Assigning to a missing key adds it. It never raises KeyError."},
    hints=["Trace the five updates one at a time. Which keys are new, which already exist?"],
    explain="coffee and samosa change in place, chai and dosa are added at the end, and the second chai changes chai to 12 without moving it.",
    trap="Moving chai to the end on its second update.")

add(id="B-4", stage="BOSS", type="coding", level="Optimize", concept="compare_types",
    challenge={
        "title": "One List, Not Two",
        "statement": "This bill keeps names and prices in two separate lists. Remove an item from one list and every later price is wrong (that is how a bill of 42 became 32). Rewrite it with <b>one dictionary</b> called <code>menu</code>. The output must stay exactly the same.",
        "input_fmt": "One line of item names separated by spaces. It may be empty.",
        "output_fmt": "One number: the total.",
        "starter": 'names = ["tea", "coffee", "samosa", "puff", "maggi"]\nprices = [12, 15, 15, 20, 30]\norder = input().split()\ntotal = 0\nfor item in order:\n    if item in names:\n        i = names.index(item)\n        total = total + prices[i]\nprint(total)\n',
        "tests": [
            {"stdin": "puff tea tea coffee", "expected": "59"},
            {"stdin": "tea dosa samosa", "expected": "27"},
            {"stdin": "maggi maggi", "expected": "60", "hidden": True, "note": "the same item twice"},
            {"stdin": "Puff", "expected": "0", "hidden": True, "note": "capital P"},
            {"stdin": "", "expected": "0", "hidden": True, "note": "empty order"},
        ],
    },
    rules=[
        {"require": r"menu\s*=\s*\{", "msg": "Make one dictionary called menu, written with { }."},
        {"forbid": r"\.index\s*\(", "msg": "Look the price up by its name in the dictionary, not with .index()."},
        {"forbid": r"\bprices\b", "msg": "Remove the separate prices list. The dictionary keeps each price with its name."},
    ],
    solution=f'menu = {MENU}\norder = input().split()\ntotal = 0\nfor item in order:\n    if item in menu:\n        total = total + menu[item]\nprint(total)\n',
    hints=["Put each name and its price together: menu = {\"tea\": 12, ...}.", "Then the price is just menu[item]. No index needed."],
    explain="One dictionary keeps each price with its name, so nothing can slip out of step. <code>menu[item]</code> replaces the index lookup.",
    trap="Keeping both lists and adding a dictionary on top does not fix the design.")

add(id="B-5", stage="BOSS", type="msq", level="Prompting", concept="membership",
    title="You ask an AI to write the Canteen Bill program. Which lines must your spec include so its code is right?",
    options=["Input: one line of item names separated by spaces.",
             "Skip any item that is not on the board; never stop with an error.",
             "Names are case-sensitive: Tea is not on the board.",
             "Example: tea dosa samosa gives 27.",
             "Make the code fast and clean.",
             "Use a list of names and a list of prices."],
    answers=[0, 1, 2, 3],
    hints=["A good spec states the input, the edge cases and a checkable example. Leave out wishes that change nothing."],
    explain="The AI needs the input format, what to do with missing items, the case rule and an example it can check against. \"Fast and clean\" changes nothing, and two lists is the bug we are escaping.",
    trap="Vague goals feel helpful but give the AI nothing to check.")

add(id="B-6", stage="BOSS", type="debug", level="Prompting", concept="add_change",
    title="An AI wrote this bill. Its totals are right, but it breaks the board. Tap the faulty line, then choose what goes wrong.",
    code=f'menu = {MENU}\norder = input().split()\ntotal = 0\nfor item in order:\n    if item not in menu:\n        menu[item] = 0\n    total = total + menu[item]\nprint(total)',
    errors=["KeyError: 'dosa'", "dosa is added to the board at price 0", "dosa is counted at 20", "TypeError"],
    line=6, error=1, focus=6,
    hints=["Totals can be right while the board is changed. What does assigning to a missing key do?"],
    explain="Line 6 assigns to a missing key, which <b>adds</b> a row: dosa now sits on the board at 0. Skip missing items with <code>if item in menu:</code> instead of writing to the board.",
    trap="Trusting the AI because the totals look right.")

GUIDE_HTML = '<h3>Reading the board · menu = {"tea": 12, "coffee": 15, "samosa": 15}</h3>\n    <div class="tscroll"><table><thead><tr><th>Expression</th><th>Gives</th><th>If the key is missing</th></tr></thead><tbody>\n      <tr><td><code>menu["tea"]</code></td><td><code>12</code></td><td><b>KeyError</b>: the program stops</td></tr>\n      <tr><td><code>menu.get("tea")</code></td><td><code>12</code></td><td><code>None</code>: the program carries on</td></tr>\n      <tr><td><code>"tea" in menu</code></td><td><code>True</code></td><td><code>False</code> (checks keys only: <code>15 in menu</code> is False)</td></tr>\n      <tr><td><code>len(menu)</code></td><td><code>3</code></td><td>counts pairs</td></tr></tbody></table></div>\n    <h3>Changing the board</h3>\n    <div class="tscroll"><table><thead><tr><th>Line</th><th>Key is new</th><th>Key is already there</th></tr></thead><tbody>\n      <tr><td><code>menu[key] = value</code></td><td>adds the pair at the <b>end</b></td><td>changes the value <b>in place</b></td></tr>\n      <tr><td><code>del menu[key]</code></td><td><b>KeyError</b></td><td>removes the whole pair</td></tr></tbody></table></div>\n    <h3>Views and loops · in the order the pairs were added</h3>\n    <div class="tscroll"><table><thead><tr><th>Code</th><th>Gives</th></tr></thead><tbody>\n      <tr><td><code>menu.keys()</code></td><td><code>dict_keys([\'tea\', \'coffee\', \'samosa\'])</code></td></tr>\n      <tr><td><code>menu.values()</code></td><td><code>dict_values([12, 15, 15])</code>, repeats kept</td></tr>\n      <tr><td><code>menu.items()</code></td><td><code>dict_items([(\'tea\', 12), (\'coffee\', 15), (\'samosa\', 15)])</code></td></tr>\n      <tr><td><code>for name in menu:</code></td><td>the keys</td></tr>\n      <tr><td><code>for name, price in menu.items():</code></td><td>each key with its value</td></tr></tbody></table></div>\n    <h3>Dictionary, list, tuple, set</h3>\n    <div class="tscroll"><table><thead><tr><th>Type</th><th>Looks like</th><th>Find an item by</th><th>Repeats</th><th>Order</th></tr></thead><tbody>\n      <tr><td>dict</td><td><code>{"tea": 12}</code></td><td>its key</td><td>keys no, values yes</td><td>insertion order</td></tr>\n      <tr><td>list</td><td><code>["tea", 12]</code></td><td>position <code>[0]</code></td><td>yes</td><td>kept</td></tr>\n      <tr><td>tuple</td><td><code>("tea", 12)</code></td><td>position <code>[0]</code>, cannot change</td><td>yes</td><td>kept</td></tr>\n      <tr><td>set</td><td><code>{"tea", "coffee"}</code></td><td><code>in</code> only</td><td>no</td><td>no fixed order</td></tr></tbody></table></div>\n    <h3>Remember</h3>\n    <ul><li><code>{}</code> is an empty <b>dictionary</b>, not a set. <code>dict()</code> makes one too.</li>\n      <li>A repeated key gives no error: the <b>last value wins</b> and the key keeps its <b>first position</b>.</li>\n      <li>Keys are case-sensitive: <code>"Tea"</code> and <code>"tea"</code> are two rows.</li>\n      <li>Brackets hold a key, never a position: <code>menu[2]</code> looks for a key named 2.</li>\n      <li><code>menu.keys()</code> is <b>live</b>; <code>list(menu.keys())</code> is a fixed <b>copy</b>.</li>\n      <li><code>dict(pairs)</code> needs two-item pairs: a flat list or a three-item element raises <b>ValueError</b>.</li>\n      <li>Keys must be immutable: a tuple works, a list raises <b>TypeError: unhashable type: \'list\'</b>. Values can be anything.</li></ul>'

# ---------------------------------------------------------------------------------------------
# Page texts, stage goals and worked examples (shown by the shared game UI)
VISUAL_PRO = ("board", "board-pro")  # solving every question of this type first try earns this badge

UI = {
    "id": "s29",
    "title": "Dictionaries: The Python Challenge",
    "short": "Dictionaries",
    "hero_h1": "Dictionaries: <em>The Python Challenge</em>",
    "hero_p": "The canteen price board is a mess: wrong prices, missing items, and a bill that charged 32 instead of 42. Master Python dictionaries, stage by stage, to fix it. Every stage is harder than the last, and the Final Boss puts it all together.",
    "story": "Agent, the canteen price board is a mess: wrong prices, missing items, and a bill that charged <b>32</b> instead of <b>42</b>. Your tool: the Python <b>dictionary</b>. Clear each stage to unlock the next. Every stage is harder than the last. Ready?",
    "lab": "board",
    "lab_name": "Dict Lab",
    "boss_win": "Board fixed!",
    "champion": "Python Dictionaries Champion",
    "guide_title": "Field guide: Python dictionaries",
    "guide_html": GUIDE_HTML,
}

# "You will learn" goals and a worked example for each stage's demo program.
# Each step highlights one line; `shows` is what that line prints (checked against real Python).
LEARN = {
    "L0": {"learn": ["Say what a key and a value are", "Read a price by its name", "Count the pairs with len()"],
           "walk": [{"line": 1, "say": "Build the board: five name tags, each with its price."},
                    {"line": 2, "say": "Find the tag maggi and read its price.", "shows": "30"},
                    {"line": 3, "say": "Curly brackets with colons make a dictionary.", "shows": "<class 'dict'>"},
                    {"line": 4, "say": "len() counts pairs, not keys and values.", "shows": "5"}]},
    "L1": {"learn": ["Make an empty dictionary", "Read a value with menu[key]", "Count pairs"],
           "walk": [{"line": 1, "say": "Empty curly brackets: an empty dictionary, not a set."},
                    {"line": 2, "say": "Python confirms the type.", "shows": "<class 'dict'>"},
                    {"line": 3, "say": "A board with two pairs."},
                    {"line": 4, "say": "The brackets hold a key, so this finds samosa's price.", "shows": "15"},
                    {"line": 5, "say": "Two pairs on the board.", "shows": "2"}]},
    "L2": {"learn": ["Predict what a repeated key does", "Add and change rows with menu[key] = value", "Delete a row and count what is left"],
           "walk": [{"line": 1, "say": "tea is written twice. No error: the last value wins, tea keeps its first place."},
                    {"line": 2, "say": "Only one tea row, now 14.", "shows": "{'tea': 14, 'coffee': 15}"},
                    {"line": 3, "say": "bun is new, so it goes on at the end."},
                    {"line": 4, "say": "coffee exists, so its value changes in place."},
                    {"line": 5, "say": "Tea with a capital T is a different key: a new row."},
                    {"line": 6, "say": "del wipes the whole bun pair."},
                    {"line": 7, "say": "The board now.", "shows": "{'tea': 14, 'coffee': 18, 'Tea': 16}"},
                    {"line": 8, "say": "Three pairs.", "shows": "3"}]},
    "L3": {"learn": ["Look up a missing key safely with get()", "Tell when in is True", "Loop over keys, values and items"],
           "walk": [{"line": 1, "say": "Three items on the board."},
                    {"line": 2, "say": "dosa is missing: get() gives None and the program carries on.", "shows": "None"},
                    {"line": 3, "say": "in checks keys only, so 15 is not found.", "shows": "False False"},
                    {"line": 4, "say": "values() keeps the repeated 15.", "shows": "[12, 15, 15]"},
                    {"line": 5, "say": "items() gives each name with its price, in order."},
                    {"line": 6, "say": "One line per pair.", "shows": "tea 12\ncoffee 15\nsamosa 15"}]},
    "L4": {"learn": ["Tell a live view from a list() copy", "Build a dictionary from pairs with dict()"],
           "walk": [{"line": 2, "say": "view is a window onto the keys: it stays live."},
                    {"line": 3, "say": "photo is a list copy taken now: it will not change."},
                    {"line": 4, "say": "samosa is added after both were made."},
                    {"line": 5, "say": "The view shows samosa too.", "shows": "dict_keys(['tea', 'coffee', 'samosa'])"},
                    {"line": 6, "say": "The copy still has two names.", "shows": "['tea', 'coffee']"},
                    {"line": 7, "say": "dict() turns two-item pairs into a board.", "shows": "{'tea': 12, 'bun': 10}"}]},
    "L5": {"learn": ["Read input and total a bill", "Skip items that are not on the board"],
           "walk": [{"line": 2, "say": "The order: tea, dosa, samosa."},
                    {"line": 5, "say": "The guard: only look up items that are on the board. dosa is skipped."},
                    {"line": 6, "say": "Add the price: 12, then 15."},
                    {"line": 7, "say": "The total.", "shows": "27"}]},
    "BOSS": {"learn": ["Trace a list of updates on a board", "Fix and rewrite real programs", "Write a spec an AI can follow"],
             "walk": [{"line": 2, "say": "Five updates, one at a time."},
                      {"line": 4, "say": "New names go on at the end; existing names change in place. chai is updated twice."},
                      {"line": 5, "say": "The final board.", "shows": "{'tea': 12, 'coffee': 18, 'samosa': 15, 'chai': 12, 'dosa': 20}"}]},
}
for _lvl in LEVELS:
    _lvl.update(LEARN.get(_lvl["id"], {}))


# ---------- Bonus Round (optional, for students who finish early) ----------
add(id="X-1", stage="BONUS", type="predict", level="Read", concept="case",
    title="What does this print?",
    code='menu = {"tea": 12, "coffee": 15}\nfor name in list(menu.keys()):\n    menu[name.upper()] = menu[name]\nprint(len(menu))',
    options=["4", "2", "!RuntimeError: dictionary changed size during iteration", "!KeyError: 'TEA'"],
    answer=0,
    why={1: "<code>\"TEA\"</code> and <code>\"tea\"</code> are different keys, so each upper-case name is a new row.",
         2: "The loop walks a <code>list()</code> copy of the keys, so adding rows is safe.",
         3: "Assigning to a missing key adds it; it never raises KeyError."},
    hints=["Is TEA the same key as tea?", "The loop walks a list copy, not the live view."],
    explain="The loop walks a fixed list copy of the keys and adds <code>TEA</code> and <code>COFFEE</code> as new keys (keys are case-sensitive): 4 pairs.")

add(id="X-2", stage="BONUS", type="numeric", level="Read", concept="membership",
    title="What number does this print?",
    code='prices = {"tea": 12, "samosa": 15, "puff": 20}\norder = ["tea", "puff", "tea", "dosa"]\nbill = 0\nfor item in order:\n    if item in prices:\n        bill = bill + prices[item]\nprint(bill)',
    value=44,
    hints=["dosa is skipped. tea is ordered twice."],
    explain="tea 12 + puff 20 + tea 12 = 44. dosa is not on the board, so the <code>if</code> skips it.")

add(id="X-3", stage="BONUS", type="tf", level="Recall", concept="hashable_keys",
    title='True or false: menu[("tea", "samosa")] = 27 adds a combo row to the board.',
    value=True,
    hints=["Can a tuple change after it is made?"],
    explain="A tuple cannot change, so it can be a key: the combo row <code>('tea', 'samosa'): 27</code> is added. A list there would raise TypeError.")

add(id="X-4", stage="BONUS", type="msq", level="Read", concept="add_change",
    title="menu = {\"tea\": 12, \"coffee\": 15}. Which lines leave the board exactly as it is?",
    options=['menu.get("dosa")', '"dosa" in menu', 'menu["coffee"] = 15', 'menu["Tea"] = 12', 'del menu["tea"]'],
    answers=[0, 1, 2],
    hints=["Looking something up never changes the board. Which lines write to it?"],
    explain='<code>get</code> and <code>in</code> only look. Setting coffee to the 15 it already has changes nothing. <code>"Tea"</code> is a new key, and <code>del</code> removes a row.')

add(id="X-5", stage="BONUS", type="predict", level="Read", concept="add_change",
    title="What does this print?",
    code='menu = {"b": 2, "a": 1}\nmenu["c"] = 3\ndel menu["b"]\nmenu["b"] = 4\nprint(list(menu.keys()))',
    options=["['a', 'c', 'b']", "['a', 'b', 'c']", "['b', 'a', 'c']", "['c', 'a', 'b']"],
    answer=0,
    why={1: "Dictionaries keep the order keys were added, not alphabetical order.",
         2: "b was deleted, so when it comes back it is a new key at the end.",
         3: "c was added after a, so a comes first."},
    hints=["A deleted key that comes back goes to the end."],
    explain="Order is the order keys were added: a, then c; b was deleted and added again, so it goes last.")

QUESTIONS = {q["id"]: q for q in Q}
LEVEL_IDS = [lvl["id"] for lvl in LEVELS]
LEVEL_BY_ID = {lvl["id"]: lvl for lvl in LEVELS}
TOTAL = sum(len(lvl["main"]) for lvl in LEVELS if not lvl.get("bonus"))  # the bonus round is optional

assert len(QUESTIONS) == len(Q), "duplicate question id"
assert TOTAL == 30 and len(Q) == 35, (TOTAL, len(Q))
for lvl in LEVELS:
    for qid in lvl["main"]:
        assert QUESTIONS[qid]["stage"] == lvl["id"], qid

# End-of-mission feedback: "What helped you learn the most?" (key, emoji, label)
FEEDBACK_HELPED = [
    ("predict", "🔮", "Predict-the-output questions"),
    ("board", "🧪", "Canteen Board builds and the Dict Lab"),
    ("debug", "🐞", "Debugging missions"),
    ("coding", "💻", "Coding challenges"),
    ("hints", "💡", "Hints and explanations"),
    ("xp", "🏆", "XP and badges"),
]

FEEDBACK_TOPIC = "Python dictionaries"
