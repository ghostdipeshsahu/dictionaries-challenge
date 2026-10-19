"""Working with Dictionaries: The Python Challenge · Session 30 mission content.

Source of truth: Session 30 deck (30_working_with_dictionaries_student_view.html), Divya's Ooty trip money sheet:
trip = {"Teja": 1500, "Ravi": 800, "Kiran": 0}; Sai joins with 0; the dhaba bill is 1200; room(name, block).

Taught (and only this): = gives the same dictionary a second name (a change through one is seen through the other,
id() is the same); copy() makes a second dictionary (a list has copy() too); len() counts pairs; in checks keys only;
clear() empties the dictionary but keeps it, while trip = {} points the name at a new one; deleting keys while
looping over the same dictionary raises RuntimeError, so loop over a copy; *args packs values into a tuple
(('Sai',), ()); * at the call opens a list (without it the list is one value); **kwargs packs name=value
arguments into a dictionary, which works like any dictionary (items(), in); ** at the call opens a dictionary,
keys must match parameter names (else TypeError); plain values fill named parameters first, the rest join the
tuple, name=value goes to the dictionary; use *args/**kwargs only when the number of arguments is unknown.

Every expected output is checked against real Python by tests/verify_s30.py.
"""

TRIP = '{"Teja": 1500, "Ravi": 800, "Kiran": 0}'

CONCEPTS = {
    "same_object": "= gives a second name",
    "copy": "copy() makes a second dictionary",
    "len_in": "len() and in",
    "clear": "clear() empties it",
    "rebind": "Change it or point at a new one",
    "loop_delete": "Deleting while looping",
    "args_tuple": "*args packs a tuple",
    "star_call": "* opens a list at the call",
    "kwargs_dict": "**kwargs packs a dictionary",
    "kwargs_use": "kwargs is a real dictionary",
    "dstar_call": "** opens a dictionary at the call",
    "landing": "Where each argument lands",
    "when_to_use": "When to use *args and **kwargs",
}

TYPE_LABEL = {
    "mcq": "Multiple choice", "msq": "Multiple select", "tf": "True or false",
    "ar": "Assertion and reasoning", "fill": "Fill in the blanks", "match": "Match the columns",
    "order": "Put in order", "categorize": "Sort into groups", "numeric": "Numeric answer",
    "predict": "Predict the output", "debug": "Debug mission", "coding": "Coding challenge",
    "land": "Where does it land?",
}

SLUG = "working-with-dictionaries"  # this mission's URL: /working-with-dictionaries/ (and /working-with-dictionaries/teacher)
MISSION_MINUTES = 45  # the clock ends the mission here and the feedback opens (MISSION_MINUTES in the environment overrides it)

XP = {"mcq": 10, "tf": 10, "predict": 15, "msq": 15, "ar": 15, "fill": 15, "numeric": 15,
      "match": 20, "order": 20, "categorize": 20, "debug": 20, "land": 25, "coding": 40}
# Seconds per question. The Session 29 class ran out of time on 17 of 30 questions (coding solved by 4% in 3 minutes),
# so questions with code get time for every line to trace: base + per line, never less than the floor.
TIME = {"mcq": 40, "tf": 25, "predict": 30, "msq": 70, "ar": 60, "fill": 40, "numeric": 30,
        "match": 60, "order": 75, "categorize": 75, "debug": 45, "land": 60, "coding": 360}
PER_LINE = {"predict": 10, "numeric": 10, "fill": 10, "debug": 10, "match": 8, "land": 10}
FLOOR = {"predict": 45, "numeric": 45, "fill": 50, "debug": 60, "land": 90}


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
    "sheet-explorer": {"name": "Sheet Explorer", "desc": "Clear Find the Copy-Cat"},
    "copy-maker": {"name": "Copy Maker", "desc": "Clear Make a Real Backup"},
    "star-packer": {"name": "Star Packer", "desc": "Clear Split the Dinner Bill"},
    "key-matcher": {"name": "Key Matcher", "desc": "Clear Who Paid What?"},
    "bug-hunter": {"name": "Bug Hunter", "desc": "Clear Fix Divya's App"},
    "trip-champion": {"name": "Working with Dictionaries Champion", "desc": "Settle the trip"},
    "combo-5": {"name": "On Fire", "desc": "5 right answers in a row"},
    "clean-sweep": {"name": "Clean Sweep", "desc": "3 stars on any stage"},
    "landing-pro": {"name": "Landing Pro", "desc": "Every \"Where does it land?\" right on the first try"},
}
STAGE_BADGE = {"L1": "sheet-explorer", "L2": "copy-maker", "L3": "star-packer", "L4": "key-matcher",
               "L5": "bug-hunter", "BOSS": "trip-champion"}
VISUAL_PRO = ("land", "landing-pro")

BOSS_SCENARIO = f'''trip = {TRIP}
backup = trip.copy()
alias = trip
alias["Kiran"] = 500

def report(*names, **paid):
    for name in names:
        print(name, paid.get(name))

report("Kiran", "Sai", **trip)
print(len(backup), backup["Kiran"])'''

LEVELS = [
    {
        "id": "L0", "name": "The Trip Sheet", "difficulty": "Warm-up",
        "job": "Meet Divya's sheet. When one friend changes it, who else sees the change?",
        "intel_title": "What you need to know",
        "intel": [
            "Sharing a sheet's <b>link</b> means everyone opens the <b>same</b> sheet. One change, everyone sees it.",
            "<b>Make a copy</b> gives you a <b>second</b> sheet. Your changes stay on your copy.",
            "Python works the same way. <code>b = trip</code> is the link. <code>trip.copy()</code> is Make a copy.",
        ],
        "demo": f'trip = {TRIP}\nb = trip\nb["Kiran"] = 500\nprint(trip["Kiran"])',
        "learn": ["Tell a shared link from a copy", "Say what changes when a dictionary has two names"],
        "walk": [{"line": 1, "say": "One sheet with three rows."},
                 {"line": 2, "say": "b is a second name for the same sheet. No new sheet is made."},
                 {"line": 3, "say": "Kiran pays 500, typed through the name b."},
                 {"line": 4, "say": "trip shows it too: there is only one sheet.", "shows": "500"}],
        "main": ["L0-1", "L0-2"],
    },
    {
        "id": "L1", "name": "Find the Copy-Cat", "difficulty": "Easy",
        "job": "Divya saved a \"backup\" of the sheet, but it keeps changing whenever the sheet changes. Find out why.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>backup = trip</code> does not make a new sheet. It gives the <b>same</b> sheet a second name.",
            "So <code>trip[\"Kiran\"] = 500</code> also shows up in <code>backup</code>. It is one sheet with two names.",
            "Want proof? <code>id(trip) == id(backup)</code> is <code>True</code> when both names point at one sheet.",
        ],
        "demo": f'trip = {TRIP}\nravi = trip\nravi["Ravi"] = 1000\nprint(trip)\nprint(id(trip) == id(ravi))',
        "learn": ["Predict what a second name sees", "Check with id() whether two names share one dictionary"],
        "walk": [{"line": 1, "say": "trip points at a sheet with three rows."},
                 {"line": 2, "say": "ravi now points at the same sheet: only an arrow is added."},
                 {"line": 3, "say": "Ravi changes his row through ravi."},
                 {"line": 4, "say": "trip sees the change: it is the same sheet.", "shows": "{'Teja': 1500, 'Ravi': 1000, 'Kiran': 0}"},
                 {"line": 5, "say": "Same id: one dictionary, two names.", "shows": "True"}],
        "main": ["L1-1", "L1-3", "L1-5", "L1-6"],
    },
    {
        "id": "L2", "name": "Make a Real Backup", "difficulty": "Easy+",
        "job": "Make a backup that stays the same when the sheet changes. Then count the sheet, empty it, and remove the friends who paid nothing, without crashing the app.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>backup = trip.copy()</code> makes a <b>real</b> backup: a second sheet that does not change when trip does.",
            "<code>len(trip)</code> counts the friends. <code>\"Ravi\" in trip</code> checks the <b>names</b> only, never the amounts.",
            "<code>trip.clear()</code> empties the sheet but keeps it. <code>trip = {}</code> starts a brand-new sheet instead.",
            "Deleting names while you loop over the same sheet crashes. Loop over <code>trip.copy()</code> and delete from <code>trip</code>.",
        ],
        "demo": f'trip = {TRIP}\nkiran = trip.copy()\nkiran["Kiran"] = 2000\nprint(trip)\ntrip.clear()\nprint(trip, len(kiran))',
        "learn": ["Make a real backup with copy()", "Use len(), in and clear()", "Delete while looping without a crash"],
        "walk": [{"line": 2, "say": "copy() makes a second sheet with the same rows."},
                 {"line": 3, "say": "Kiran types 2000 in his own copy."},
                 {"line": 4, "say": "trip still has Kiran's 0.", "shows": "{'Teja': 1500, 'Ravi': 800, 'Kiran': 0}"},
                 {"line": 5, "say": "clear() empties trip. The dictionary is still there."},
                 {"line": 6, "say": "trip is empty; the copy still has 3 rows.", "shows": "{} 3"}],
        "main": ["L2-2", "L2-3", "L2-4", "L2-6", "L2-7"],
    },
    {
        "id": "L3", "name": "Split the Dinner Bill", "difficulty": "Medium",
        "job": "The dinner bill is 1200 rupees. Write one split() that works for 3 friends, 4 friends, or 10.",
        "intel_title": "What you need to know",
        "intel": [
            "Put a <code>*</code> before a parameter: <code>def split(bill, *friends):</code>. Now it takes <b>any number</b> of friends.",
            "Python packs those friends into a tuple: <code>split(1200, \"Teja\", \"Ravi\")</code> gives <code>friends = ('Teja', 'Ravi')</code>.",
            "Names already in a list? Open it with a <code>*</code> in the call: <code>split(1200, *table)</code>.",
        ],
        "demo": 'def show(*friends):\n    print(friends)\n\nshow("Teja", "Ravi", "Kiran")\nshow("Sai")\nshow()',
        "learn": ["Write a function that takes any number of values", "Predict the tuple *args makes", "Open a list into separate values with *"],
        "walk": [{"line": 1, "say": "*friends will collect every value given to show()."},
                 {"line": 4, "say": "Three values: one tuple of three.", "shows": "('Teja', 'Ravi', 'Kiran')"},
                 {"line": 5, "say": "One value: still a tuple, with a comma.", "shows": "('Sai',)"},
                 {"line": 6, "say": "No values: an empty tuple.", "shows": "()"}],
        "main": ["L3-1", "L3-2", "L3-3", "L3-4", "L3-7"],
    },
    {
        "id": "L4", "name": "Who Paid What?", "difficulty": "Hard",
        "job": "Send everyone's name and amount into one function, like Teja=1500, Ravi=800, however many friends there are.",
        "intel_title": "What you need to know",
        "intel": [
            "Two stars, <code>def mark_paid(**paid):</code>, collect <code>name=value</code> pairs into a <b>dictionary</b>: <code>{'Teja': 1500, 'Ravi': 800}</code>.",
            "It is a normal dictionary, so <code>paid.items()</code> and <code>\"Ravi\" in paid</code> work on it.",
            "Have a dictionary already? <code>room(**data)</code> opens it. Each key must match a parameter's name.",
            "Know exactly how many values there are? Then just name them. Use <code>*</code> and <code>**</code> only when you can't know.",
        ],
        "demo": 'def mark_paid(**paid):\n    print(paid)\n\nmark_paid(Teja=1500, Ravi=800)\n\ndef room(name, block):\n    print(name, block)\n\nroom(**{"block": "C", "name": "Teja"})',
        "learn": ["Collect name=value arguments with **kwargs", "Open a dictionary into a call with **", "Choose between fixed parameters, *args and **kwargs"],
        "walk": [{"line": 1, "say": "**paid will collect every name=value argument into a dictionary."},
                 {"line": 4, "say": "Each name becomes a key, each value its value.", "shows": "{'Teja': 1500, 'Ravi': 800}"},
                 {"line": 9, "say": "** opens the dictionary: each key goes to the parameter with its name, whatever the order.", "shows": "Teja C"}],
        "main": ["L4-1", "L4-2", "L4-4", "L4-6", "L4-7"],
    },
    {
        "id": "L5", "name": "Fix Divya's App", "difficulty": "Hard",
        "job": "Divya's trip app has three bugs. Fix each one so the app works for every friend, not just the examples.",
        "intel_title": "Before you start",
        "intel": [
            "Each fix reads input and prints. The sample tests show what it should print.",
            "Hidden tests try tricky cases, like an empty sheet or a friend who paid nothing.",
            "Some fixes also check <b>how</b> you solved it, for example that split() really uses <code>*friends</code>.",
        ],
        "demo": f'trip = {{"Teja": 1500, "Kiran": 0, "Ravi": 800, "Sai": 0}}\nbackup = trip.copy()\nfor name in backup.keys():\n    if trip[name] == 0:\n        del trip[name]\nprint(trip)',
        "learn": ["Make a backup that really keeps the old sheet", "Delete safely while looping", "Write and call functions with *args and **kwargs"],
        "walk": [{"line": 2, "say": "Make a copy to loop over."},
                 {"line": 3, "say": "Walk the copy: it never changes."},
                 {"line": 5, "say": "Delete from the real sheet. Kiran and Sai go."},
                 {"line": 6, "say": "Only the payers are left.", "shows": "{'Teja': 1500, 'Ravi': 800}"}],
        "main": ["L5-1", "L5-4"],
    },
    {
        "id": "BOSS", "name": "Settle the Trip", "difficulty": "Boss",
        "job": "Everything comes together: a backup, a second name, and a function that checks who has paid. Settle the trip.",
        "intel_title": "Before you start",
        "intel": [
            "Read the program on the left one line at a time.",
            "For each line, ask: does it <b>change</b> a sheet, or does it give a name to a sheet?",
            "Last two jobs: tell an AI exactly what you want, then spot what its code gets wrong.",
        ],
        "demo": BOSS_SCENARIO,
        "learn": ["Trace names, copies and arguments together", "Fix and rewrite real programs", "Write a spec an AI can follow"],
        "walk": [{"line": 2, "say": "backup is a real copy: a second sheet."},
                 {"line": 3, "say": "alias is a second name for trip's sheet."},
                 {"line": 4, "say": "Kiran pays 500 through alias: trip changes, backup does not."},
                 {"line": 10, "say": "\"Kiran\" and \"Sai\" go into names; **trip opens trip into name=value arguments for paid."},
                 {"line": 8, "say": "Kiran is a key in paid: 500. Sai is not: get() gives None.", "shows": "Kiran 500\nSai None"},
                 {"line": 11, "say": "The backup still has 3 rows and Kiran's 0.", "shows": "3 0"}],
        "main": ["B-1", "B-3", "B-5", "B-6", "B-7"],
    },
]

# ---------------------------------------------------------------------------------------------
Q = []


def add(**q):
    q.setdefault("xp", XP[q["type"]])
    q.setdefault("time", timer(q))
    Q.append(q)


# ---------- L0 · Mission Briefing ----------
add(id="L0-1", stage="L0", type="mcq", level="Recall", concept="same_object",
    title="Ravi opens the shared link to Divya's sheet and changes his 800 to 1000. Divya has the same link open. What does she see?",
    options=["1000", "800", "Both 800 and 1000, in two rows", "An error: two people cannot edit one sheet"],
    answer=0,
    why={1: "A shared link is the <b>same</b> sheet, not a second one. Ravi's change is on it.",
         2: "There is one row for Ravi, on one sheet. Changing it replaces the value.",
         3: "Everyone with the link edits the one sheet."},
    hints=["A link opens the same sheet. How many sheets are there?"],
    explain="Divya and Ravi look at <b>one</b> sheet, so she sees 1000. In Python, <code>ravi = trip</code> works the same way.",
    trap="Thinking a shared link is a separate copy.")

add(id="L0-2", stage="L0", type="tf", level="Recall", concept="copy",
    title="True or false: after Kiran taps Make a copy, typing in his copy does not change Divya's sheet.",
    value=True,
    hints=["Make a copy creates a second sheet. Is Kiran typing in Divya's sheet?"],
    explain="Make a copy gives a <b>second</b> sheet, so Divya's sheet keeps its numbers. In Python that is <code>trip.copy()</code>.")

# ---------- L1 · One Sheet, Two Names ----------
add(id="L1-1", stage="L1", type="predict", level="Read", concept="same_object",
    title="What does this print?",
    code=f'trip = {TRIP}\nravi = trip\nravi["Ravi"] = 1000\nprint(trip)',
    options=["{'Teja': 1500, 'Ravi': 1000, 'Kiran': 0}", "{'Teja': 1500, 'Ravi': 800, 'Kiran': 0}",
             "{'Teja': 1500, 'Ravi': 800, 'Kiran': 0, 'Ravi': 1000}", "!NameError: name 'ravi' is not defined"],
    answer=0,
    why={1: "<code>ravi = trip</code> is not a copy. Both names point at one dictionary, so the change shows through <code>trip</code>.",
         2: "Ravi is already a key, so his value changes in place. Keys never repeat.",
         3: "Line 2 creates the name ravi."},
    hints=["How many dictionaries does line 2 make?"],
    explain="Line 2 gives the same dictionary a second name. Changing Ravi's value through <code>ravi</code> changes the one dictionary, so <code>trip</code> shows 1000.",
    trap="Thinking <code>ravi = trip</code> makes a copy, so trip is unchanged.")

add(id="L1-3", stage="L1", type="numeric", level="Read", concept="same_object",
    title="What number does this print?",
    code=f'trip = {TRIP}\nb = trip\nb["Kiran"] = 500\nprint(trip["Kiran"])',
    value=500,
    hints=["b is another name for trip's dictionary."],
    explain="<code>b</code> and <code>trip</code> are one dictionary. Setting Kiran to 500 through <code>b</code> is seen through <code>trip</code>: 500.",
    trap="Answering 0, as if <code>b = trip</code> had made a copy.")

add(id="L1-5", stage="L1", type="order", level="Implement", concept="same_object",
    title="Put the lines in order so the program prints {'Teja': 1500, 'Ravi': 1000}, then 2.",
    items=['print(len(trip))', 'ravi["Ravi"] = 1000', 'trip = {"Teja": 1500, "Ravi": 800}', 'print(trip)', 'ravi = trip'],
    mapping=[2, 4, 1, 3, 0],
    expect="{'Teja': 1500, 'Ravi': 1000}\n2",
    hints=["A name has to exist before you can use it.", "trip shows 1000 only after the change through ravi."],
    explain="Make the dictionary, give it the second name, change Ravi through that name, then print: trip shows the change, and it still has 2 pairs.")

add(id="L1-6", stage="L1", type="predict", level="Read", concept="same_object",
    title="Divya's \"backup\". What does print(backup) show?",
    code='trip = {"Ravi": 800, "Kiran": 0}\nbackup = trip\ntrip["Kiran"] = 500\nprint(backup)',
    options=["{'Ravi': 800, 'Kiran': 500}", "{'Ravi': 800, 'Kiran': 0}", "{'Ravi': 800}", "!KeyError: 'Kiran'"],
    answer=0,
    why={1: "<code>backup = trip</code> only gives the same sheet a second name. It is not a backup.",
         2: "Nothing deletes a row here.",
         3: "Kiran is a key on the sheet."},
    hints=["Is backup a second sheet, or a second name?"],
    explain="<code>backup</code> and <code>trip</code> are one dictionary, so the change to Kiran shows through <code>backup</code>. A real backup needs <code>trip.copy()</code>.",
    trap="Thinking <code>backup = trip</code> keeps the old values.")

# ---------- L2 · Copy, Clear, Count ----------
add(id="L2-2", stage="L2", type="predict", level="Read", concept="clear",
    title="What does this print?",
    code=f'trip = {TRIP}\nprint(len(trip))\nprint(800 in trip)\nprint("Ravi" in trip)\ntrip.clear()\nprint(trip)\nprint(len(trip))',
    options=["3\nFalse\nTrue\n{}\n0", "3\nTrue\nTrue\n{}\n0", "3\nFalse\nTrue\n{'Teja': 0, 'Ravi': 0, 'Kiran': 0}\n3",
             "3\nFalse\nTrue\n!NameError: name 'trip' is not defined"],
    answer=0,
    why={1: "<code>in</code> checks the <b>keys</b> only. 800 is a value.",
         2: "<code>clear()</code> removes the rows. It does not set the values to 0.",
         3: "<code>clear()</code> empties the dictionary; the name <code>trip</code> still exists."},
    hints=["in looks at the names only.", "clear() empties the sheet. Does the sheet itself vanish?"],
    explain="3 pairs; 800 is a value, so <code>800 in trip</code> is False; \"Ravi\" is a key, True. <code>clear()</code> leaves an empty dictionary <code>{}</code> with 0 pairs.",
    trap="Thinking <code>in</code> also searches the amounts.")

add(id="L2-3", stage="L2", type="categorize", level="Read", concept="rebind",
    title='Each line starts from trip = {"Ravi": 800, "Kiran": 0}. What does print(backup) show after it?',
    items=['backup = trip; trip["Kiran"] = 500', 'backup = trip.copy(); trip["Kiran"] = 500',
           'backup = trip; trip.clear()', 'backup = trip; trip = {}', 'backup = trip.copy(); trip.clear()'],
    categories=["{'Ravi': 800, 'Kiran': 500}", "{'Ravi': 800, 'Kiran': 0}", "{}"],
    mapping=[0, 1, 2, 1, 1],
    setup='trip = {"Ravi": 800, "Kiran": 0}',
    hints=["Ask of each line: does it change the dictionary, or point a name at a new one?", "clear() changes the dictionary itself. trip = {} only moves the name trip."],
    explain="With <code>backup = trip</code> both names share one dictionary, so a change or <code>clear()</code> shows in backup. A copy keeps its own pairs. <code>trip = {}</code> points <code>trip</code> at a new empty dictionary and leaves the old one, still named backup, untouched.",
    trap="<code>trip = {}</code> looks like <code>clear()</code>, but it only moves the name.")

add(id="L2-4", stage="L2", type="msq", level="Read", concept="len_in",
    title=f"trip = {TRIP}. Which of these print True?",
    options=['print("Ravi" in trip)', "print(800 in trip)", "print(len(trip) == 3)", 'print("Sai" in trip)', "print(0 in trip.values())"],
    answers=[0, 2, 4],
    hints=["in checks keys. values() gives the amounts."],
    explain='"Ravi" is a key, <code>len(trip)</code> is 3, and 0 is one of the values. 800 is a value, not a key, and Sai is not on the sheet.',
    trap="Expecting <code>800 in trip</code> to be True.")

add(id="L2-6", stage="L2", type="match", level="Read", concept="copy",
    title="Match each expression to its value.",
    code=f'trip = {TRIP}\nkiran = trip.copy()\nravi = trip\nravi["Ravi"] = 1000\nkiran["Kiran"] = 2000',
    left=['trip["Ravi"]', 'kiran["Ravi"]', 'trip["Kiran"]', "id(trip) == id(ravi)", "id(trip) == id(kiran)"],
    right=["True", "0", "False", "800", "1000"],
    mapping=[4, 3, 1, 0, 2],
    setup=f'trip = {TRIP}\nkiran = trip.copy()\nravi = trip\nravi["Ravi"] = 1000\nkiran["Kiran"] = 2000',
    hints=["kiran was copied before Ravi changed his amount.", "ravi is a second name for trip."],
    explain="<code>ravi</code> shares trip's dictionary, so trip sees Ravi's 1000 and the ids match. <code>kiran</code> is a copy made earlier: it still has Ravi's 800, its change to Kiran stays in it, and its id differs.")

add(id="L2-7", stage="L2", type="debug", level="Debug", concept="loop_delete",
    title="Divya removes everyone who paid 0, and Python stops. Tap the line where it stops, then choose what goes wrong.",
    code='trip = {"Teja": 1500, "Kiran": 0, "Ravi": 800, "Sai": 0}\nfor name in trip.keys():\n    if trip[name] == 0:\n        del trip[name]\nprint(trip)',
    errors=["RuntimeError: dictionary changed size during iteration", "KeyError: 'Kiran'", "It prints {'Teja': 1500, 'Ravi': 800}", "TypeError"],
    line=2, error=0, focus=2,
    hints=["The loop walks trip while line 4 deletes from trip.", "Which line asks for the next key after a deletion?"],
    explain="After <code>del</code> removes Kiran, the loop on line 2 asks the same dictionary for its next key, and Python stops: <code>RuntimeError: dictionary changed size during iteration</code>. Loop over <code>trip.copy()</code> instead.",
    trap="Expecting the deletes to just work.")

# ---------- L3 · Any Number of Friends ----------
add(id="L3-1", stage="L3", type="predict", level="Read", concept="args_tuple",
    title="What does this print?",
    code='def show(*friends):\n    print(friends)\n\nshow("Teja", "Ravi", "Kiran")\nshow("Sai")\nshow()',
    options=["('Teja', 'Ravi', 'Kiran')\n('Sai',)\n()", "['Teja', 'Ravi', 'Kiran']\n['Sai']\n[]",
             "Teja Ravi Kiran\nSai", "('Teja', 'Ravi', 'Kiran')\n('Sai')\n()"],
    answer=0,
    why={1: "<code>*friends</code> packs a <b>tuple</b> (round brackets), not a list.",
         2: "<code>print(friends)</code> prints the tuple itself, brackets and quotes included.",
         3: "A one-item tuple is printed with a comma: <code>('Sai',)</code>."},
    hints=["*friends always packs into one kind of collection, even with one value or none."],
    explain="Every value given to <code>*friends</code> goes into one tuple: three names, one name with its comma, or none at all, <code>()</code>.",
    trap="Thinking <code>*friends</code> packs a list.")

add(id="L3-2", stage="L3", type="land", level="Read", concept="landing",
    title="Where does each argument of this call land?",
    code='def split(bill, *friends):\n    print(friends)\n\nsplit(1200, "Teja", "Ravi", "Kiran")',
    boxes=["bill", "*friends"],
    args=["1200", '"Teja"', '"Ravi"', '"Kiran"'],
    mapping=[0, 1, 1, 1],
    prints="('Teja', 'Ravi', 'Kiran')",
    hints=["Values with no name fill the named parameters first, left to right."],
    explain="1200 fills <code>bill</code>, the first named parameter. The names left over go into the tuple <code>friends</code>: it prints <code>('Teja', 'Ravi', 'Kiran')</code>.")

add(id="L3-3", stage="L3", type="predict", level="Read", concept="star_call",
    title="The names are already in a list. What does this print?",
    code='def split(bill, *friends):\n    share = bill // len(friends)\n    for name in friends:\n        print(name, share)\n\ntable = ["Teja", "Ravi", "Kiran"]\nsplit(1200, table)',
    options=["['Teja', 'Ravi', 'Kiran'] 1200", "Teja 400\nRavi 400\nKiran 400", "!TypeError: split() takes 2 positional arguments", "Teja 1200\nRavi 1200\nKiran 1200"],
    answer=0,
    why={1: "Without <code>*</code> at the call, the list goes in as <b>one</b> value. friends is a tuple holding one list.",
         2: "<code>*friends</code> takes any number of values, including one.",
         3: "There is one item in friends, so the loop prints once."},
    hints=["Without a * at the call, how many values does split() receive after the bill?"],
    explain="<code>table</code> is passed as one value, so <code>friends</code> is <code>(['Teja', 'Ravi', 'Kiran'],)</code>. len is 1, the share is 1200, and the one item printed is the whole list. Write <code>split(1200, *table)</code> to open it.",
    trap="Thinking a list goes in as separate values even without <code>*</code>.")

add(id="L3-4", stage="L3", type="fill", level="Implement", concept="star_call",
    title="Fill the gaps so one split() shares the bill between everyone in the list: Teja 400, Ravi 400, Kiran 400.",
    code='def split(bill, ___friends):\n    share = bill // len(friends)\n    for name in friends:\n        print(name, share)\n\ntable = ["Teja", "Ravi", "Kiran"]\nsplit(1200, ___table)',
    blanks=[["*"], ["*"]],
    expect="Teja 400\nRavi 400\nKiran 400",
    hints=["One star in the def collects the values.", "One star at the call opens the list."],
    explain="<code>*friends</code> in the def collects the values into a tuple; <code>*table</code> at the call opens the list into three separate values.")

add(id="L3-7", stage="L3", type="ar", level="Read", concept="args_tuple",
    title="Read the assertion and the reason.",
    assertion='def show(*friends): print(friends). Then show("Sai") prints (\'Sai\',).',
    reason="*friends always packs the values into a tuple, and a tuple with one item is written with a comma.",
    options=AR_OPTIONS, answer=0,
    why={1: "R is exactly why the output has round brackets and a comma.",
         2: "R is true: even one value is packed into a tuple.",
         3: "A is true: Python prints ('Sai',)."},
    hints=["What does one value packed by *friends look like?"],
    explain="Both are true and R explains A: one value still becomes a tuple, and Python shows a one-item tuple with a comma.")

# ---------- L4 · Name = Value ----------
add(id="L4-1", stage="L4", type="predict", level="Read", concept="kwargs_dict",
    title="What does this print?",
    code='def mark_paid(**paid):\n    print(paid)\n\nmark_paid(Teja=1500, Ravi=800)\nmark_paid()',
    options=["{'Teja': 1500, 'Ravi': 800}\n{}", "(1500, 800)\n()", "('Teja', 'Ravi')\n()", "{'Teja': 1500, 'Ravi': 800}\n!TypeError: mark_paid() missing argument"],
    answer=0,
    why={1: "<code>**paid</code> packs a <b>dictionary</b>, not a tuple of values.",
         2: "The names become keys, and the values stay with them.",
         3: "<code>**paid</code> accepts none at all: it is then <code>{}</code>."},
    hints=["Two stars collect name=value arguments. Into what?"],
    explain="Each <code>name=value</code> becomes a key and its value in one dictionary. With no arguments, paid is an empty dictionary <code>{}</code>.",
    trap="Thinking <code>**paid</code> packs a tuple, like <code>*friends</code>.")

add(id="L4-2", stage="L4", type="predict", level="Read", concept="kwargs_use",
    title="What does this print?",
    code='def mark_paid(**paid):\n    for name, amount in paid.items():\n        print(name, "paid", amount)\n    print("Ravi" in paid)\n\nmark_paid(Teja=1500, Ravi=800)',
    options=["Teja paid 1500\nRavi paid 800\nTrue", "!AttributeError: 'tuple' object has no attribute 'items'",
             "Teja paid 1500\nRavi paid 800\nFalse", "1500 paid Teja\n800 paid Ravi\nTrue"],
    answer=0,
    why={1: "paid is a dictionary, so <code>items()</code> works.",
         2: "\"Ravi\" is a key in paid, so <code>in</code> gives True.",
         3: "items() gives (key, value): the name first."},
    hints=["paid is a dictionary. What works on any dictionary?"],
    explain="<code>paid</code> is a real dictionary: <code>items()</code> loops over name and amount, and <code>\"Ravi\" in paid</code> checks the keys: True.",
    trap="Thinking paid is a tuple of values, so <code>items()</code> fails.")

add(id="L4-4", stage="L4", type="predict", level="Read", concept="dstar_call",
    title="The room card is a dictionary, written block first. What does this print?",
    code='def room(name, block):\n    print(name, block)\n\ndata = {"block": "C", "name": "Teja"}\nroom(**data)',
    options=["Teja C", "C Teja", "!TypeError: room() takes 2 positional arguments", "{'block': 'C', 'name': 'Teja'}"],
    answer=0,
    why={1: "<code>**</code> fills parameters by <b>name</b>, not by place. The order of the keys does not matter.",
         2: "The keys match the parameter names exactly, so there is no error.",
         3: "<code>**data</code> opens the dictionary into separate arguments."},
    hints=["** turns each key into a name=value argument. Which parameter does block=\"C\" go to?"],
    explain="<code>room(**data)</code> is <code>room(block=\"C\", name=\"Teja\")</code>. Each value goes to the parameter with its name, so it prints <code>Teja C</code>.",
    trap="Thinking ** fills the parameters by place.")

add(id="L4-6", stage="L4", type="land", level="Read", concept="landing",
    title="Where does each argument of this call land?",
    code='def mark_paid(**paid):\n    print(paid)\n\nmark_paid("Teja", 1500)',
    boxes=["**paid"],
    args=['"Teja"', "1500"],
    mapping=[1, 1],
    prints="!TypeError: mark_paid() takes 0 positional arguments but 2 were given",
    hints=["**paid only collects name=value arguments. Are there any here?"],
    explain="Both values are plain, with no name, and mark_paid() has no parameter for plain values. Neither has a box, so Python stops with <code>TypeError: mark_paid() takes 0 positional arguments but 2 were given</code>. Write <code>mark_paid(Teja=1500)</code>.",
    trap="Expecting <code>{'Teja': 1500}</code>.")

add(id="L4-7", stage="L4", type="categorize", level="Read", concept="when_to_use",
    title="Which kind of parameters fits each job?",
    items=["Split the dhaba bill among the friends at the table", "Print one student's room: name and block",
           "Save any extra details a student types: phone, blood group, anything", "Add up all of today's trip expenses",
           "Area of the hostel room: length and width"],
    categories=["Fixed parameters", "*args", "**kwargs"],
    mapping=[1, 0, 2, 1, 0],
    hints=["Can you say how many values there will be? Do they come with names?"],
    explain="When you know how many values there are (name and block; length and width), name each parameter. Any number of plain values: <code>*args</code>. Any number of name=value details: <code>**kwargs</code>.",
    trap="Reaching for *args when the number of values is known.")

# ---------- L5 · Code Breaker ----------
add(id="L5-1", stage="L5", type="coding", level="Debug", concept="copy",
    challenge={
        "title": "Divya's Backup",
        "statement": "Divya keeps a backup before anyone pays. Read one name and amount and put it on the sheet. Then print the <b>backup</b> and then the sheet. The backup must still show the sheet as it was before the change. The starter's backup is not a backup: fix it.",
        "input_fmt": "One line: a name and a whole-number amount.",
        "output_fmt": "Two lines: print(backup), then print(trip).",
        "starter": f'trip = {TRIP}\nbackup = trip\nname, amount = input().split()\ntrip[name] = int(amount)\nprint(backup)\nprint(trip)\n',
        "tests": [
            {"stdin": "Kiran 500", "expected": "{'Teja': 1500, 'Ravi': 800, 'Kiran': 0}\n{'Teja': 1500, 'Ravi': 800, 'Kiran': 500}"},
            {"stdin": "Ravi 1000", "expected": "{'Teja': 1500, 'Ravi': 800, 'Kiran': 0}\n{'Teja': 1500, 'Ravi': 1000, 'Kiran': 0}"},
            {"stdin": "Sai 300", "expected": "{'Teja': 1500, 'Ravi': 800, 'Kiran': 0}\n{'Teja': 1500, 'Ravi': 800, 'Kiran': 0, 'Sai': 300}", "hidden": True, "note": "a new name joins"},
            {"stdin": "Teja 1500", "expected": "{'Teja': 1500, 'Ravi': 800, 'Kiran': 0}\n{'Teja': 1500, 'Ravi': 800, 'Kiran': 0}", "hidden": True, "note": "the same amount again"},
        ],
    },
    solution=f'trip = {TRIP}\nbackup = trip.copy()\nname, amount = input().split()\ntrip[name] = int(amount)\nprint(backup)\nprint(trip)\n',
    hints=["Run the first sample: why does the backup show 500?", "Change line 2 so backup is a second dictionary."],
    explain="<code>backup = trip</code> only gave the sheet a second name. <code>backup = trip.copy()</code> makes a second dictionary, so the change on line 4 leaves it as it was.",
    trap="Copying after the change keeps nothing old.")

add(id="L5-4", stage="L5", type="coding", level="Extend", concept="dstar_call",
    challenge={
        "title": "The Trip Total",
        "statement": "trip_total(**paid) prints the total and how many paid 0. The starter reads Divya's whole sheet into a dictionary, but the call stops with <code>TypeError</code>. Fix the call so the sheet's names and amounts go in as name=value arguments.",
        "input_fmt": "First line: N. Then N lines, each a name and a whole-number amount.",
        "output_fmt": "One line: the total and the number who paid 0.",
        "starter": 'def trip_total(**paid):\n    total = 0\n    unpaid = 0\n    for name, amount in paid.items():\n        total = total + amount\n        if amount == 0:\n            unpaid = unpaid + 1\n    print(total, unpaid)\n\nn = int(input())\nsheet = {}\nfor i in range(n):\n    name, amount = input().split()\n    sheet[name] = int(amount)\ntrip_total(sheet)\n',
        "tests": [
            {"stdin": "4\nTeja 1500\nRavi 800\nKiran 0\nSai 0", "expected": "2300 2"},
            {"stdin": "3\nTeja 1500\nRavi 800\nKiran 0", "expected": "2300 1"},
            {"stdin": "0", "expected": "0 0", "hidden": True, "note": "an empty sheet"},
            {"stdin": "2\nTeja 1500\nRavi 800", "expected": "2300 0", "hidden": True, "note": "everyone paid"},
            {"stdin": "2\nKiran 0\nSai 0", "expected": "0 2", "hidden": True, "note": "nobody paid"},
        ],
    },
    rules=[{"require": r"trip_total\s*\(\s*\*\*\s*\w+\s*\)", "msg": "Call trip_total with the sheet opened by **."}],
    solution='def trip_total(**paid):\n    total = 0\n    unpaid = 0\n    for name, amount in paid.items():\n        total = total + amount\n        if amount == 0:\n            unpaid = unpaid + 1\n    print(total, unpaid)\n\nn = int(input())\nsheet = {}\nfor i in range(n):\n    name, amount = input().split()\n    sheet[name] = int(amount)\ntrip_total(**sheet)\n',
    hints=["trip_total() takes no plain values, only name=value arguments.", "** at the call opens a dictionary into name=value arguments."],
    explain="<code>trip_total(sheet)</code> passes one plain value, and **paid cannot take plain values. <code>trip_total(**sheet)</code> opens the sheet so each name and amount goes in as name=value.",
    trap="Thinking the unpaid count stays 1, as in the first sample.")

# ---------- Final Boss ----------
add(id="B-1", stage="BOSS", type="predict", level="Read", concept="kwargs_use", scenario=True,
    title="Run the scenario on the left. What does it print?",
    options=["Kiran 500\nSai None\n3 0", "Kiran 0\nSai None\n3 0", "Kiran 500\nSai None\n3 500", "Kiran 500\n!KeyError: 'Sai'"],
    answer=0,
    why={1: "alias is a second name for trip, so Kiran's 500 is on trip's dictionary, which **trip opens.",
         2: "backup was copied before the change, so it keeps Kiran's 0.",
         3: "<code>paid.get(name)</code> gives None for a missing key; it never raises KeyError."},
    hints=["Which dictionaries does the change through alias reach?", "get() on a missing key gives None."],
    explain="<code>alias</code> shares trip's dictionary, so Kiran is 500 in it; <code>**trip</code> passes that into paid. Sai is not a key, so <code>get</code> gives None. backup is a copy taken earlier: 3 rows, Kiran 0.",
    trap="Thinking the change through alias reaches the backup.")

add(id="B-3", stage="BOSS", type="land", level="Read", concept="landing",
    title="Divya checks who has paid. Where does each argument land?",
    code='def show_paid(*names, **paid):\n    for name in names:\n        if name in paid:\n            print(name, paid[name])\n\nshow_paid("Teja", Ravi=800, Teja=1500)',
    boxes=["*names", "**paid"],
    args=['"Teja"', "Ravi=800", "Teja=1500"],
    mapping=[0, 1, 1],
    prints="Teja 1500",
    hints=["A plain value and a name=value can both mention Teja. Where does each kind go?"],
    explain="The plain <code>\"Teja\"</code> joins the tuple names; both name=value arguments go into the dictionary paid. Teja is a key in paid, so it prints <code>Teja 1500</code>.",
    trap="Thinking the plain \"Teja\" and Teja=1500 clash.")

add(id="B-5", stage="BOSS", type="coding", level="Optimize", concept="args_tuple",
    challenge={
        "title": "One Split for All",
        "statement": "Someone wrote split3 and split4, and picks one by the number of friends. It breaks for 2 or 5 friends. Replace them with <b>one</b> split(bill, *friends). The output must stay exactly the same for 3 and 4 friends, and now work for any number.",
        "input_fmt": "First line: the bill. Second line: the friends' names (at least one).",
        "output_fmt": "One line per friend: the name and the share (bill // number of friends).",
        "starter": 'def split3(bill, a, b, c):\n    for name in (a, b, c):\n        print(name, bill // 3)\n\ndef split4(bill, a, b, c, d):\n    for name in (a, b, c, d):\n        print(name, bill // 4)\n\nbill = int(input())\nnames = input().split()\nif len(names) == 3:\n    split3(bill, names[0], names[1], names[2])\nelif len(names) == 4:\n    split4(bill, names[0], names[1], names[2], names[3])\n',
        "tests": [
            {"stdin": "1200\nTeja Ravi Kiran", "expected": "Teja 400\nRavi 400\nKiran 400"},
            {"stdin": "1200\nTeja Ravi Kiran Sai", "expected": "Teja 300\nRavi 300\nKiran 300\nSai 300"},
            {"stdin": "900\nTeja Ravi", "expected": "Teja 450\nRavi 450", "hidden": True, "note": "two friends"},
            {"stdin": "1000\nTeja Ravi Kiran Sai Divya", "expected": "Teja 200\nRavi 200\nKiran 200\nSai 200\nDivya 200", "hidden": True, "note": "five friends"},
        ],
    },
    rules=[
        {"forbid": r"\bsplit[34]\b", "msg": "Remove split3 and split4: one function is enough."},
        {"require": r"def\s+split\s*\(\s*\w+\s*,\s*\*\w+\s*\)", "msg": "Define one split(bill, *friends)."},
    ],
    solution='def split(bill, *friends):\n    for name in friends:\n        print(name, bill // len(friends))\n\nbill = int(input())\nnames = input().split()\nsplit(bill, *names)\n',
    hints=["What does *friends collect, and how do you count it?", "Call it once: split(bill, *names)."],
    explain="One <code>split(bill, *friends)</code> covers every count: <code>len(friends)</code> replaces the 3 and the 4, and <code>split(bill, *names)</code> replaces the if/elif.",
    trap="Adding split2 and split5 keeps the problem.")

add(id="B-6", stage="BOSS", type="msq", level="Prompting", concept="when_to_use",
    title="You ask an AI for a function that adds up the trip's expenses. Which lines must your spec include so its code is right?",
    options=["It takes any number of amounts: def total(*amounts).",
             "Example: total(1500, 800, 0) prints 2300.",
             "With no amounts, total() prints 0.",
             "It prints one whole number.",
             "Make it short and smart.",
             "It takes exactly three amounts a, b and c."],
    answers=[0, 1, 2, 3],
    hints=["A good spec gives the signature, what it prints, an example and the edge case. Wishes give the AI nothing to check."],
    explain="The AI needs the signature (<code>*amounts</code>, since the count is unknown), what to print, a checkable example and the empty case. \"Short and smart\" changes nothing, and three fixed amounts is the bug we are avoiding.",
    trap="Leaving out the empty case: total() with nothing at all.")

add(id="B-7", stage="BOSS", type="debug", level="Prompting", concept="loop_delete",
    title="An AI wrote this to remove the unpaid, \"with a backup to loop over\". Python still stops. Tap the line that must be changed, then choose what goes wrong.",
    code=f'trip = {{"Teja": 1500, "Kiran": 0, "Ravi": 800}}\nbackup = trip\nfor name in backup.keys():\n    if backup[name] == 0:\n        del trip[name]\nprint(trip)',
    errors=["RuntimeError: dictionary changed size during iteration", "KeyError: 'Kiran'", "Nothing: it prints {'Teja': 1500, 'Ravi': 800}", "TypeError"],
    line=2, error=0, focus=2,
    hints=["Is backup a second dictionary, or a second name for trip?"],
    explain="Line 2 only gives trip a second name, so the loop still walks the dictionary it deletes from, and Python stops with <code>RuntimeError</code>. Change it to <code>backup = trip.copy()</code>.",
    trap="Trusting the word \"backup\" in the AI's code.")

QUESTIONS = {q["id"]: q for q in Q}
LEVEL_IDS = [lvl["id"] for lvl in LEVELS]
LEVEL_BY_ID = {lvl["id"]: lvl for lvl in LEVELS}
TOTAL = sum(len(lvl["main"]) for lvl in LEVELS)

GUIDE_HTML = """<h3>Names and copies · trip = {"Teja": 1500, "Ravi": 800, "Kiran": 0}</h3>
    <div class="tscroll"><table><thead><tr><th>Line</th><th>What it does</th><th>trip after b["Kiran"] = 500</th></tr></thead><tbody>
      <tr><td><code>b = trip</code></td><td>a <b>second name</b> for the same dictionary</td><td>changed: Kiran is 500</td></tr>
      <tr><td><code>b = trip.copy()</code></td><td>a <b>second dictionary</b> with the same pairs</td><td>unchanged: Kiran is 0</td></tr></tbody></table></div>
    <h3>Count, check, empty</h3>
    <div class="tscroll"><table><thead><tr><th>Code</th><th>Gives</th></tr></thead><tbody>
      <tr><td><code>len(trip)</code></td><td><code>3</code>: the number of pairs</td></tr>
      <tr><td><code>"Ravi" in trip</code></td><td><code>True</code>: in checks <b>keys</b> only (<code>800 in trip</code> is False)</td></tr>
      <tr><td><code>trip.clear()</code></td><td>empties it: <code>{}</code>. The dictionary stays, and every name for it sees <code>{}</code></td></tr>
      <tr><td><code>trip = {}</code></td><td>points <code>trip</code> at a <b>new</b> empty dictionary; other names keep the old one</td></tr></tbody></table></div>
    <h3>Any number of arguments</h3>
    <div class="tscroll"><table><thead><tr><th>Where</th><th>Code</th><th>Means</th></tr></thead><tbody>
      <tr><td>def</td><td><code>def split(bill, *friends):</code></td><td>extra plain values packed into a <b>tuple</b>: <code>('Sai',)</code>, <code>()</code></td></tr>
      <tr><td>def</td><td><code>def mark_paid(**paid):</code></td><td>name=value arguments packed into a <b>dictionary</b>: <code>{'Teja': 1500}</code>, <code>{}</code></td></tr>
      <tr><td>call</td><td><code>split(1200, *table)</code></td><td>opens the list into separate values</td></tr>
      <tr><td>call</td><td><code>room(**data)</code></td><td>opens the dictionary into name=value; keys must match parameter names</td></tr></tbody></table></div>
    <h3>Remember</h3>
    <ul><li>Plain values fill the named parameters first, left to right; what is left joins <code>*args</code>. name=value goes to <code>**kwargs</code>, by name, never by place.</li>
      <li>A plain value with no box (no <code>*args</code>), or a name that matches no parameter (no <code>**kwargs</code>), stops Python with <b>TypeError</b>.</li>
      <li>Deleting keys while looping over the same dictionary stops with <b>RuntimeError</b>. Loop over a <code>copy()</code>.</li>
      <li>Use <code>*args</code> and <code>**kwargs</code> only when you cannot say how many arguments there will be.</li></ul>"""

UI = {
    "id": "s30",
    "title": "Working with Dictionaries: The Python Challenge",
    "short": "Working with Dicts",
    "hero_h1": "Mission: <em>Settle the Ooty Trip</em>",
    "hero_p": "Divya and her friends just got back from Ooty. Divya kept everyone's money in one shared sheet, and now it is a mess: numbers change by themselves, the app crashes, and nobody knows who owes what. Help her fix it, one stage at a time.",
    "story": """<p><b>Divya and her friends just got back from Ooty.</b> She kept everyone's money in one shared sheet. Now it's a mess: numbers changed by themselves, the app crashed, and nobody knows who owes what.</p>
      <h3>Your 3 jobs</h3>
      <ol><li>🔍 <b>Find the copy-cat.</b> Divya made a "backup", but it keeps changing with the sheet. Why?</li>
        <li>🧹 <b>Clean the sheet.</b> Remove friends who paid nothing, without crashing the app.</li>
        <li>🍽️ <b>Split the dinner bill.</b> Make it work for 3 friends, 4 friends, or 10.</li></ol>
      <p class="win">You win when every stage is cleared and the trip is settled.</p>""",
    "lab": "trip",
    "lab_name": "Trip Lab",
    "boss_win": "Trip settled!",
    "champion": "Working with Dictionaries Champion",
    "guide_title": "Field guide: working with dictionaries",
    "guide_html": GUIDE_HTML,
}

assert len(QUESTIONS) == len(Q), "duplicate question id"
assert TOTAL == len(Q) == 28, TOTAL
for lvl in LEVELS:
    for qid in lvl["main"]:
        assert QUESTIONS[qid]["stage"] == lvl["id"], qid

# End-of-mission feedback: "What helped you learn the most?" (key, emoji, label)
FEEDBACK_HELPED = [
    ("predict", "🔮", "Predict-the-output questions"),
    ("land", "📦", "Where does it land? questions"),
    ("lab", "🧪", "The Trip Lab"),
    ("debug", "🐞", "Debugging missions"),
    ("coding", "💻", "Coding challenges"),
    ("hints", "💡", "Hints and explanations"),
    ("xp", "🏆", "XP and badges"),
]

FEEDBACK_TOPIC = "working with dictionaries"
