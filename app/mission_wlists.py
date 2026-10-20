"""Working with Lists: The Python Challenge · Session 8.2 mission content.

Source of truth: the Working with Lists deck (79 slides). Its examples: a = "Hello"; a = a + " World" gives a new id;
list_a = [1, 2, 3] and list_b = [1, 2, 3] have two ids; list_b = list_a has one id; list_b[3] = 4 shows in both;
list_a = [6, 7] and list_a = list_a + [6, 7] leave list_b as [1, 2]; list_a += [6, 7] changes the list in place,
so list_b is [1, 2, 6, 7]; list_b = [3, list_a] then list_a[1] = 4 gives [3, [1, 4]]; a = 2; list_a = [1, a];
a = 3 leaves [1, 2]. Daily Challenge: animals += wild_animals adds two items; animals += [wild_animals] adds one.

Taught (and only this): anything in a variable is an object; every object gets a unique id, tied to where it sits in
memory, and the number can change each run; id() finds it; changing an item by index keeps the same list;
= gives the same list a second name (a reference), so a change through one name shows through the other;
= with a new list moves only that one name; + makes a new list; += changes the list in place; a list inside
a list is the same object, so its changes show; ints and strings cannot change in place, so a = 3 never
reaches a list that holds the old value.
Known before: variables, int/float/str, input(), print, if/else, for/while, range, len, str(), creating lists,
indexing, list_a[i] = x, += [x], list(range(n)). Not used: list methods, slicing, is, sum/min/max, f-strings.

Every expected output is checked against real Python by tests/verify_wlists.py.
"""

SONGS = '["Naatu Naatu", "Jai Ho", "Kesariya"]'

CONCEPTS = {
    "object_id": "Every object has an id",
    "id_compare": "Compare ids with id()",
    "change_item": "Change an item by index",
    "assign_shares": "= gives a second name",
    "shared_change": "One change, both names see it",
    "reassign": "A new list moves one name",
    "concat_new": "+ makes a new list",
    "plus_equal": "+= changes the list in place",
    "nested_mutable": "A list inside a list",
    "immutable_item": "Numbers and strings don't follow",
    "add_one_item": "+= x vs += [x]",
}

TYPE_LABEL = {
    "mcq": "Multiple choice", "msq": "Multiple select", "tf": "True or false",
    "ar": "Assertion and reasoning", "fill": "Fill in the blanks", "match": "Match the columns",
    "order": "Put in order", "categorize": "Sort into groups", "numeric": "Numeric answer",
    "predict": "Predict the output", "debug": "Debug mission", "coding": "Coding challenge",
}

ORDER = 1  # where this session sits in the course (session pickers list them in this order)
SLUG = "working-with-lists"  # this mission's URL: /working-with-lists/ (and /working-with-lists/teacher)
MISSION_MINUTES = 45  # the clock ends the mission here and the feedback opens (MISSION_MINUTES in the environment overrides it)

XP = {"mcq": 10, "tf": 10, "predict": 15, "msq": 15, "ar": 15, "fill": 15, "numeric": 15,
      "match": 20, "order": 20, "categorize": 20, "debug": 20, "coding": 40}
# Seconds per question, the Session 30 rule: questions with code get time for every line to trace,
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
    "id-detective": {"name": "ID Detective", "desc": "Clear Who Has the Real Playlist?"},
    "change-tracker": {"name": "Change Tracker", "desc": "Clear One Change, Two Names"},
    "in-place-pro": {"name": "In-Place Pro", "desc": "Clear New List or Same List?"},
    "box-master": {"name": "Box Master", "desc": "Clear Lists Inside Lists"},
    "bug-hunter": {"name": "Bug Hunter", "desc": "Clear Fix Meera's App"},
    "lists-champion": {"name": "Working with Lists Champion", "desc": "Save Fresher's Night"},
    "combo-5": {"name": "On Fire", "desc": "5 right answers in a row"},
    "clean-sweep": {"name": "Clean Sweep", "desc": "3 stars on any stage"},
    "bug-spotter": {"name": "Bug Spotter", "desc": "Every debug mission right on the first try"},
}
STAGE_BADGE = {"L1": "id-detective", "L2": "change-tracker", "L3": "in-place-pro", "L4": "box-master",
               "L5": "bug-hunter", "BOSS": "lists-champion"}
VISUAL_PRO = ("debug", "bug-spotter")  # solving every question of this type first try earns this badge

BOSS_SCENARIO = '''playlist = ["Naatu Naatu", "Jai Ho"]
rahul = playlist
anu = playlist + ["Kesariya"]
dj = ["Intro", playlist]
rahul += ["Malhari"]
playlist[0] = "Butta Bomma"
print(len(anu), len(dj))
print(dj)'''

LEVELS = [
    {
        "id": "L0", "name": "The Shared Playlist", "difficulty": "Warm-up",
        "job": "Meet Meera's Fresher's Night playlist. When one friend changes it, who else sees the change?",
        "intel_title": "What you need to know",
        "intel": [
            "A shared playlist <b>link</b> opens the <b>same</b> playlist for everyone. One change, everyone sees it.",
            "Making your <b>own</b> playlist with the same songs gives a <b>second</b> playlist. Same songs, but not the same playlist.",
            "Python works the same way. <code>rahul = playlist</code> is the shared link: one list, two names.",
        ],
        "demo": f'playlist = {SONGS}\nrahul = playlist\nrahul[2] = "Butta Bomma"\nprint(playlist)',
        "learn": ["Tell a shared list from a second list", "Say what changes when a list has two names"],
        "walk": [{"line": 1, "say": "One playlist with three songs."},
                 {"line": 2, "say": "rahul is a second name for the same list. No new list is made."},
                 {"line": 3, "say": "Rahul swaps the third song (index 2) through his name."},
                 {"line": 4, "say": "playlist shows it too: there is only one list.", "shows": "['Naatu Naatu', 'Jai Ho', 'Butta Bomma']"}],
        "main": ["L0-1", "L0-2"],
    },
    {
        "id": "L1", "name": "Who Has the Real Playlist?", "difficulty": "Easy",
        "job": "Rahul and Anu both say they have Meera's playlist. Use id() to find out who really shares it.",
        "intel_title": "What you need to know",
        "intel": [
            "Each object gets a unique <b>id</b> when it is made. It is tied to where the object sits in memory, and it can be a different number every run.",
            "<code>id(playlist)</code> gives that id. <code>id(a) == id(b)</code> is <code>True</code> only when both names point at <b>one</b> object.",
            "Two lists with the same songs are still <b>two</b> lists, with two ids.",
        ],
        "demo": f'playlist = {SONGS}\nrahul = playlist\nanu = {SONGS}\nprint(id(playlist) == id(rahul))\nprint(id(playlist) == id(anu))',
        "learn": ["Use id() to see an object's identity", "Tell whether two names share one list"],
        "walk": [{"line": 1, "say": "Meera's playlist: one list object, with its own id."},
                 {"line": 2, "say": "rahul points at that same list."},
                 {"line": 3, "say": "Anu types the same three songs. That makes a new list, with a new id."},
                 {"line": 4, "say": "Same id: one list, two names.", "shows": "True"},
                 {"line": 5, "say": "Different ids: same songs, but two lists.", "shows": "False"}],
        "main": ["L1-1", "L1-2", "L1-3", "L1-4"],
    },
    {
        "id": "L2", "name": "One Change, Two Names", "difficulty": "Easy+",
        "job": "Rahul kept a \"backup\" with backup = playlist. Meera swapped one song, and the backup changed too. Show Rahul why.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>playlist[1] = \"Malhari\"</code> changes the item at index 1. It is still the same list, with the same id.",
            "<code>rahul = playlist</code> does not make a new list. It gives the same list a second name: a second <b>reference</b>.",
            "So a change through <b>either</b> name shows through both. One list, two names.",
        ],
        "demo": 'list_a = [1, 2, 3, 5]\nlist_b = list_a\nlist_b[3] = 4\nprint("list a : " + str(list_a))\nprint("list b : " + str(list_b))',
        "learn": ["Change a list item by its index", "Predict what a second name sees after a change"],
        "walk": [{"line": 1, "say": "One list with four numbers."},
                 {"line": 2, "say": "list_b is a second name for the same list."},
                 {"line": 3, "say": "Index 3 changes from 5 to 4, through list_b."},
                 {"line": 4, "say": "list_a sees it: it is the same list.", "shows": "list a : [1, 2, 3, 4]"},
                 {"line": 5, "say": "And list_b, of course.", "shows": "list b : [1, 2, 3, 4]"}],
        "main": ["L2-1", "L2-2", "L2-3", "L2-5"],
    },
    {
        "id": "L3", "name": "New List or Same List?", "difficulty": "Medium",
        "job": "Anu added two songs, but Rahul can't see them. Meera added them another way, and everyone could. Find the difference.",
        "intel_title": "What you need to know",
        "intel": [
            "<code>list_a = [6, 7]</code> points list_a at a <b>brand-new</b> list. Other names keep the old one.",
            "<code>list_a = list_a + [6, 7]</code>: the <code>+</code> builds a <b>new</b> list, then <code>=</code> moves list_a to it. list_b still has <code>[1, 2]</code>.",
            "<code>list_a += [6, 7]</code> changes the list <b>itself</b> (in place). Every name for it sees <code>[1, 2, 6, 7]</code>.",
        ],
        "demo": 'list_a = [1, 2]\nlist_b = list_a\nlist_a = list_a + [6, 7]\nprint("list b : " + str(list_b))\nlist_b += [6, 7]\nprint("list b : " + str(list_b))',
        "learn": ["Tell = with a new list from a change in place", "Predict what + and += do to every name"],
        "walk": [{"line": 2, "say": "Two names, one list [1, 2]."},
                 {"line": 3, "say": "+ builds a new list [1, 2, 6, 7]. Only list_a moves to it."},
                 {"line": 4, "say": "list_b still points at the old list.", "shows": "list b : [1, 2]"},
                 {"line": 5, "say": "+= adds 6 and 7 to list_b's own list, in place."},
                 {"line": 6, "say": "Now list_b's list has four items.", "shows": "list b : [1, 2, 6, 7]"}],
        "main": ["L3-1", "L3-2", "L3-3", "L3-4", "L3-5"],
    },
    {
        "id": "L4", "name": "Lists Inside Lists", "difficulty": "Hard",
        "job": "DJ Karthik keeps a request list that holds Meera's playlist inside it. Work out what follows a change, and what doesn't.",
        "intel_title": "What you need to know",
        "intel": [
            'A list can hold another list: <code>dj = ["Intro", playlist]</code> holds the playlist itself (a reference), not a copy. So <code>playlist[0] = "Malhari"</code> shows inside <code>dj</code> too.',
            "Numbers and strings can't be changed in place. <code>a = 3</code> points a at a new object; a list that holds the old 2 keeps 2.",
            "<code>+=</code> adds each item of a list: <code>animals += wild_animals</code> adds two items. <code>animals += [wild_animals]</code> adds the whole list as <b>one</b> item.",
        ],
        "demo": 'list_a = [1, 2]\nlist_b = [3, list_a]\nlist_a[1] = 4\nprint(list_b)\na = 2\nlist_c = [1, a]\na = 3\nprint(list_c)',
        "learn": ["Predict changes to a list inside a list", "Know why a = 3 never reaches a list", "Add a whole list as one item with += [x]"],
        "walk": [{"line": 2, "say": "list_b holds 3 and the list list_a itself."},
                 {"line": 3, "say": "Index 1 of list_a changes: 2 becomes 4."},
                 {"line": 4, "say": "list_b sees it: its second item is that same list.", "shows": "[3, [1, 4]]"},
                 {"line": 6, "say": "list_c holds 1 and the number 2."},
                 {"line": 7, "say": "a now points at a new number 3. The list still holds 2."},
                 {"line": 8, "say": "No change in list_c.", "shows": "[1, 2]"}],
        "main": ["L4-1", "L4-2", "L4-3", "L4-4", "L4-5"],
    },
    {
        "id": "L5", "name": "Fix Meera's App", "difficulty": "Hard",
        "job": "DJ Karthik's set list in Meera's app is broken. Fix it so it works for every playlist, not just the examples.",
        "intel_title": "Before you start",
        "intel": [
            "Your fix reads input and prints. Sample tests show the output; hidden tests try tricky cases, like no friends yet or a friend who sends no songs.",
        ],
        "demo": 'set_list = []\nblock = ["Naatu Naatu", "Jai Ho"]\nset_list += [block]\nset_list += block\nprint(set_list)\nprint(len(set_list))',
        "learn": ["Make a backup that really keeps the old songs", "Add a list as one item, and give each item its own list"],
        "walk": [{"line": 3, "say": "+= [block] adds the whole block as one item."},
                 {"line": 4, "say": "+= block adds its two songs one by one."},
                 {"line": 5, "say": "One block, then two loose songs.", "shows": "[['Naatu Naatu', 'Jai Ho'], 'Naatu Naatu', 'Jai Ho']"},
                 {"line": 6, "say": "Three items in all.", "shows": "3"}],
        "main": ["L5-2"],
    },
    {
        "id": "BOSS", "name": "Save Fresher's Night", "difficulty": "Boss",
        "job": "Everything comes together: a second name, a new list, a list inside a list, and +=. Save the night.",
        "intel_title": "Before you start",
        "intel": [
            "Read the program on the left line by line. For each line, ask: does it change a list, or does it point a name at a list?",
            "Last job: tell an AI exactly what you want, so its code does not break the playlist.",
        ],
        "demo": BOSS_SCENARIO,
        "learn": ["Trace names, new lists and changes in place together", "Fix and rewrite real programs", "Write a spec an AI can follow"],
        "walk": [{"line": 2, "say": "rahul is a second name for the playlist."},
                 {"line": 3, "say": "+ makes a new list for anu: three songs, all her own."},
                 {"line": 4, "say": "dj holds \"Intro\" and the playlist itself."},
                 {"line": 5, "say": "+= adds Malhari to the playlist in place: rahul, playlist and dj all see it. anu does not."},
                 {"line": 6, "say": "Index 0 changes in the same list."},
                 {"line": 7, "say": "anu still has 3 songs; dj still has 2 items.", "shows": "3 2"},
                 {"line": 8, "say": "The list inside dj shows both changes.", "shows": "['Intro', ['Butta Bomma', 'Jai Ho', 'Malhari']]"}],
        "main": ["B-1", "B-2", "B-3", "B-4"],
    },
]

# ---------------------------------------------------------------------------------------------
Q = []


def add(**q):
    q.setdefault("xp", XP[q["type"]])
    q.setdefault("time", timer(q))
    Q.append(q)


# ---------- L0 · The Shared Playlist ----------
add(id="L0-1", stage="L0", type="mcq", level="Recall", concept="assign_shares",
    title="Rahul opens Meera's shared playlist link and swaps the third song for Butta Bomma. Meera has the same link open. What is the third song on her screen?",
    options=["Butta Bomma", "Kesariya", "Both, as two songs", "An error: two people cannot change one playlist"],
    answer=0,
    why={1: "A shared link is the <b>same</b> playlist, not a second one. Rahul's change is on it.",
         2: "Rahul swapped the song. There is still one third song, on one playlist.",
         3: "Everyone with the link changes the one playlist."},
    hints=["A link opens the same playlist. How many playlists are there?"],
    explain="Meera and Rahul look at <b>one</b> playlist, so she sees Butta Bomma. In Python, <code>rahul = playlist</code> works the same way.",
    trap="Thinking a shared link is a separate copy.")

add(id="L0-2", stage="L0", type="tf", level="Recall", concept="id_compare",
    title="True or false: Anu makes her own new playlist with the same three songs. When she swaps a song in hers, Meera's playlist does not change.",
    value=True,
    hints=["Anu made a second playlist. Is she changing Meera's?"],
    explain="Anu's playlist has the same songs, but it is a <b>second</b> playlist, so Meera's keeps its songs. In Python, two lists typed with the same items are two objects with two ids.")

# ---------- L1 · Who Has the Real Playlist? ----------
add(id="L1-1", stage="L1", type="predict", level="Read", concept="id_compare",
    title="What does this print?",
    code='playlist = ["Naatu Naatu", "Jai Ho"]\nanu = ["Naatu Naatu", "Jai Ho"]\nprint(id(playlist) == id(anu))\nanu = playlist\nprint(id(playlist) == id(anu))',
    options=["False\nTrue", "True\nTrue", "True\nFalse", "False\nFalse"],
    answer=0,
    why={1: "Line 2 types a <b>new</b> list. Same songs, but a different object with a different id.",
         2: "The first check compares two separate lists: False. After <code>anu = playlist</code> they share one: True.",
         3: "Line 4 points anu at Meera's list, so the second check is True."},
    hints=["How many lists exist after line 2? After line 4, where does anu point?"],
    explain="Lines 1 and 2 make two lists with the same songs: two objects, two ids, so False. <code>anu = playlist</code> points anu at Meera's list: one object, so True.",
    trap="Thinking the same songs mean the same list.")

add(id="L1-2", stage="L1", type="mcq", level="Recall", concept="object_id",
    title="Meera runs print(id(playlist)) today, and runs the same program again tomorrow. Which is true?",
    options=["The number is always the same: it is the playlist's number in the class",
             "The number may be different: the id is given when the list is made, and it is tied to where it sits in memory",
             "It prints the songs' index numbers: 0, 1, 2",
             "id() works only on lists, not on numbers or strings"],
    answer=1,
    why={0: "An id is not fixed for ever. The deck says it can be different each time you run the program.",
         2: "id() gives <b>one</b> number for the whole object, not the indexes of its items.",
         3: "Every object has an id: <code>id(5)</code>, <code>id(\"A\")</code> and <code>id(1.25)</code> all work."},
    hints=["Where does an object's id come from, and does a new run make new objects?"],
    explain="Each run makes new objects in memory, and each gets an id tied to where it is stored. So never memorise an id: compare ids <b>within</b> one run.",
    trap="Thinking an id is a fixed number you can remember.")

add(id="L1-3", stage="L1", type="msq", level="Read", concept="id_compare",
    title="Which of these print True?",
    code=f'playlist = {SONGS}\nrahul = playlist\nanu = {SONGS}\ndj = rahul',
    options=["print(id(playlist) == id(rahul))", "print(id(playlist) == id(anu))", "print(id(dj) == id(playlist))",
             "print(id(anu) == id(rahul))", "print(id(dj) == id(rahul))"],
    answers=[0, 2, 4],
    hints=["Count the lists: line 1 makes one, line 3 makes another. Which names point at the first?"],
    explain="playlist, rahul and dj all point at the list from line 1, so any two of them share one id. anu typed a new list, so its id differs from all three.",
    trap="Expecting anu's list to match because the songs are the same.")

add(id="L1-4", stage="L1", type="ar", level="Read", concept="object_id",
    title="Read the assertion and the reason.",
    assertion='a = "Hello", then a = a + " World". print(id(a)) before and after this prints two different numbers.',
    reason='a + " World" makes a new string object, "Hello World", and = points a at it.',
    options=AR_OPTIONS, answer=0,
    why={1: "R is exactly why the id changes: a now names a different object.",
         2: "R is true: a string cannot change in place, so + builds a new one.",
         3: "A is true: the deck's run shows two different ids."},
    hints=["Does + change \"Hello\", or make something new?"],
    explain="Both are true and R explains A: <code>a + \" World\"</code> builds a new object with its own id, and <code>=</code> moves the name a to it.")

# ---------- L2 · One Change, Two Names ----------
add(id="L2-1", stage="L2", type="predict", level="Read", concept="shared_change",
    title="Rahul's \"backup\". What does print(backup) show?",
    code=f'playlist = {SONGS}\nbackup = playlist\nplaylist[2] = "Butta Bomma"\nprint(backup)',
    options=["['Naatu Naatu', 'Jai Ho', 'Butta Bomma']", "['Naatu Naatu', 'Jai Ho', 'Kesariya']",
             "['Naatu Naatu', 'Jai Ho', 'Kesariya', 'Butta Bomma']", "!IndexError: list assignment index out of range"],
    answer=0,
    why={1: "<code>backup = playlist</code> only gives the same list a second name. It is not a backup.",
         2: "<code>playlist[2] = ...</code> replaces the item at index 2. It does not add one.",
         3: "Index 2 is the third song, and there are three songs."},
    hints=["Is backup a second list, or a second name?"],
    explain="<code>backup</code> and <code>playlist</code> are one list, so the swap at index 2 shows through <code>backup</code>.",
    trap="Thinking <code>backup = playlist</code> keeps the old songs.")

add(id="L2-2", stage="L2", type="numeric", level="Read", concept="change_item",
    title="Song votes. What number does this print?",
    code='votes = [5, 3, 8]\nv = votes\nv[1] = v[1] + 4\nvotes[0] = 6\nprint(votes[1] + v[0])',
    value=13,
    hints=["v and votes are one list. Track it after each line.", "After line 4 the list is [6, ?, 8]."],
    explain="v and votes share one list. Line 3 makes index 1 into 7, line 4 makes index 0 into 6, so the list is [6, 7, 8] through both names: 7 + 6 = 13.",
    trap="Answering 12 (3 + 4 + 5), as if v were a separate list.")

add(id="L2-3", stage="L2", type="fill", level="Implement", concept="assign_shares",
    title="Fill the gaps so both lines print ['Naatu Naatu', 'Malhari', 'Kesariya'].",
    code=f'playlist = {SONGS}\nrahul = ___\nrahul[___] = "Malhari"\nprint(playlist)\nprint(rahul)',
    blanks=[["playlist"], ["1", "-2"]],
    expect="['Naatu Naatu', 'Malhari', 'Kesariya']\n['Naatu Naatu', 'Malhari', 'Kesariya']",
    hints=["rahul must be a second name for the same list.", "Jai Ho sits at index 1."],
    explain="<code>rahul = playlist</code> gives the list a second name, and <code>rahul[1] = \"Malhari\"</code> changes that one list, so both prints show Malhari.")

add(id="L2-5", stage="L2", type="order", level="Implement", concept="shared_change",
    title="Put the lines in order so the program prints [5, 3, 9], then 3.",
    items=['rahul = votes', 'print(votes)', 'votes = [5, 3, 8]', 'print(len(rahul))', 'rahul[2] = 9'],
    mapping=[2, 0, 4, 1, 3],
    expect="[5, 3, 9]\n3",
    hints=["A name has to exist before you can use it.", "votes shows 9 only after the change through rahul."],
    explain="Make the list, give it the second name, change index 2 through that name, then print: votes shows the change, and the list still has 3 items.")

# ---------- L3 · New List or Same List? ----------
add(id="L3-1", stage="L3", type="predict", level="Read", concept="reassign",
    title="Meera starts a fresh playlist. What does this print?",
    code='playlist = ["Naatu Naatu", "Jai Ho"]\nrahul = playlist\nplaylist = ["Malhari", "Kesariya"]\nprint(playlist)\nprint(rahul)',
    options=["['Malhari', 'Kesariya']\n['Naatu Naatu', 'Jai Ho']", "['Malhari', 'Kesariya']\n['Malhari', 'Kesariya']",
             "['Naatu Naatu', 'Jai Ho', 'Malhari', 'Kesariya']\n['Naatu Naatu', 'Jai Ho']",
             "['Naatu Naatu', 'Jai Ho']\n['Naatu Naatu', 'Jai Ho']"],
    answer=0,
    why={1: "Line 3 makes a <b>new</b> list and moves only the name playlist to it. rahul still points at the old list.",
         2: "= with a new list replaces what playlist points at. It does not add to the old list.",
         3: "playlist now points at the new list, so the first line shows the new songs."},
    hints=["Does line 3 change the old list, or make a new one?"],
    explain="Line 3 builds a brand-new list and points <code>playlist</code> at it. The old list is untouched, and <code>rahul</code> still points at it.",
    trap="Thinking = with a new list changes every name.")

add(id="L3-2", stage="L3", type="predict", level="Read", concept="plus_equal",
    title="Meera adds a song with +=. What does this print?",
    code='playlist = ["Naatu Naatu", "Jai Ho"]\nrahul = playlist\nplaylist += ["Malhari"]\nprint(rahul)\nprint(len(playlist))',
    options=["['Naatu Naatu', 'Jai Ho', 'Malhari']\n3", "['Naatu Naatu', 'Jai Ho']\n3",
             "['Naatu Naatu', 'Jai Ho', 'Malhari']\n2", "['Naatu Naatu', 'Jai Ho', ['Malhari']]\n3"],
    answer=0,
    why={1: "<code>+=</code> changes the list in place. rahul points at that same list, so he sees Malhari.",
         2: "The list now has three songs, so len is 3.",
         3: "+= adds the <b>items</b> of [\"Malhari\"]: one song, not a list inside the list."},
    hints=["Does += make a new list, or change the one both names share?"],
    explain="<code>playlist += [\"Malhari\"]</code> updates the object in place. rahul and playlist are one list, so both see three songs.",
    trap="Treating += like = with +, which would leave rahul behind.")

add(id="L3-3", stage="L3", type="categorize", level="Read", concept="concat_new",
    title="Each line starts from list_a = [1, 2] and list_b = list_a. What does print(list_b) show after it?",
    items=['list_a += [6, 7]', 'list_a = list_a + [6, 7]', 'list_a[1] = 6', 'list_b = list_b + [6, 7]', 'list_a = [6, 7]'],
    categories=["[1, 2]", "[1, 2, 6, 7]", "[1, 6]"],
    mapping=[1, 0, 2, 1, 0],
    setup='list_a = [1, 2]\nlist_b = list_a',
    hints=["Ask of each line: does it change the shared list, or point one name at a new list?", "Watch which name moves. If list_b itself moves, print(list_b) shows the new list."],
    explain="+= and changing an index both change the shared list, so list_b sees it. <code>list_a = list_a + [6, 7]</code> and <code>list_a = [6, 7]</code> move only list_a. <code>list_b = list_b + [6, 7]</code> moves list_b itself to the new list, so it shows <code>[1, 2, 6, 7]</code>.",
    trap="Putting <code>list_b = list_b + [6, 7]</code> under [1, 2]: here the name that moves is list_b.")

add(id="L3-4", stage="L3", type="match", level="Read", concept="concat_new",
    title="Match each expression to its value.",
    code='list_a = [1, 2]\nlist_b = list_a\nlist_c = list_a + [6]\nlist_b += [7]',
    left=["list_a", "list_c", "id(list_a) == id(list_b)", "id(list_a) == id(list_c)", "len(list_b)"],
    right=["False", "[1, 2, 6]", "3", "True", "[1, 2, 7]"],
    mapping=[4, 1, 3, 0, 2],
    setup='list_a = [1, 2]\nlist_b = list_a\nlist_c = list_a + [6]\nlist_b += [7]',
    hints=["list_c was made by + before 7 was added.", "list_b is a second name for list_a."],
    explain="<code>list_c = list_a + [6]</code> builds a new list <code>[1, 2, 6]</code> with its own id. <code>list_b += [7]</code> changes the list list_a and list_b share, so list_a is <code>[1, 2, 7]</code>, their ids match, and it has 3 items.")

add(id="L3-5", stage="L3", type="mcq", level="Implement", concept="plus_equal",
    title="Earlier, Meera wrote rahul = playlist. Which line adds Malhari so that playlist and rahul both show it?",
    options=['playlist = playlist + ["Malhari"]', 'playlist += ["Malhari"]', 'playlist = ["Malhari"]', 'rahul = rahul + ["Malhari"]'],
    answer=1,
    why={0: "+ builds a new list and moves only playlist to it. rahul keeps the old songs.",
         2: "This points playlist at a new list with one song. rahul keeps the old list.",
         3: "Now rahul moves to a new list. playlist does not get Malhari."},
    hints=["Only one of these changes the list in place."],
    explain="<code>+=</code> changes the shared list itself, so every name for it shows Malhari. The other three all make a new list and move just one name.",
    trap="Picking <code>playlist = playlist + [...]</code> because it prints the same for playlist.")

# ---------- L4 · Lists Inside Lists ----------
add(id="L4-1", stage="L4", type="predict", level="Read", concept="nested_mutable",
    title="DJ Karthik's request list holds Meera's playlist. What does this print?",
    code='playlist = ["Naatu Naatu", "Jai Ho"]\ndj = ["Intro", playlist]\nplaylist[1] = "Malhari"\nprint(dj)',
    options=["['Intro', ['Naatu Naatu', 'Malhari']]", "['Intro', ['Naatu Naatu', 'Jai Ho']]",
             "['Intro', 'Naatu Naatu', 'Malhari']", "['Malhari', ['Naatu Naatu', 'Jai Ho']]"],
    answer=0,
    why={1: "dj holds the playlist <b>itself</b>, not a copy. The change at index 1 shows inside dj.",
         2: "A list inside a list keeps its own brackets: dj has two items, the second one is a list.",
         3: "Line 3 changes index 1 of playlist, not of dj."},
    hints=["What is dj's second item: a copy of the songs, or the playlist list itself?"],
    explain="<code>dj = [\"Intro\", playlist]</code> stores a reference to the playlist. Changing an item of the playlist changes that one list, so dj shows <code>['Naatu Naatu', 'Malhari']</code> inside it.",
    trap="Thinking dj took a snapshot of the songs.")

add(id="L4-2", stage="L4", type="predict", level="Read", concept="immutable_item",
    title="A song name in a variable. What does this print?",
    code='song = "Jai Ho"\nplaylist = ["Naatu Naatu", song]\nsong = "Malhari"\nprint(playlist)\nprint(song)',
    options=["['Naatu Naatu', 'Jai Ho']\nMalhari", "['Naatu Naatu', 'Malhari']\nMalhari",
             "['Naatu Naatu', 'Jai Ho']\nJai Ho", "['Naatu Naatu', 'song']\nMalhari"],
    answer=0,
    why={1: "A string can't change in place. Line 3 points song at a new string; the list still holds \"Jai Ho\".",
         2: "song itself now names \"Malhari\", so the second print shows Malhari.",
         3: "The list holds the value of song, \"Jai Ho\", not the word song."},
    hints=["Does line 3 change the string \"Jai Ho\", or point song at a new string?"],
    explain="The list holds the string \"Jai Ho\" itself. <code>song = \"Malhari\"</code> only moves the name song to a new string, so the list does not change. Same as the deck's <code>a = 3</code>.",
    trap="Thinking the list follows the variable song.")

add(id="L4-3", stage="L4", type="debug", level="Debug", concept="add_one_item",
    title="Daily Challenge: the expected output is ['cat', 'dog', ['Tiger', 'Fox']]. Tap the line with the mistake, then choose what the code prints instead.",
    code="animals = ['cat', 'dog']\nwild_animals = ['Tiger', 'Fox']\nanimals += wild_animals\nprint(animals)",
    errors=["It prints ['cat', 'dog', 'Tiger', 'Fox']", "It prints ['cat', 'dog', ['Tiger', 'Fox']]: there is no mistake",
            "TypeError: 'list' object is not callable", "It prints ['Tiger', 'Fox']"],
    line=3, error=0, focus=3,
    hints=["+= adds each item of the list on its right.", "To add one item that is a list, wrap it in brackets."],
    explain="<code>animals += wild_animals</code> adds the two animals one by one: <code>['cat', 'dog', 'Tiger', 'Fox']</code>. Write <code>animals += [wild_animals]</code> to add the whole list as one item.",
    trap="Thinking += adds the list as one item.")

add(id="L4-4", stage="L4", type="fill", level="Implement", concept="add_one_item",
    title="Fill the gap so Anu's two songs go in as ONE item: ['Intro', 'Naatu Naatu', ['Malhari', 'Kesariya']], then 3.",
    code='dj = ["Intro", "Naatu Naatu"]\nanu = ["Malhari", "Kesariya"]\ndj += ___\nprint(dj)\nprint(len(dj))',
    blanks=[["[anu]", "[ anu ]"]],
    expect="['Intro', 'Naatu Naatu', ['Malhari', 'Kesariya']]\n3",
    hints=["dj += anu would add two songs, one by one.", "Wrap anu in brackets to make it a single item."],
    explain="<code>dj += [anu]</code> adds a list with one item, and that item is anu's list. So dj gets 3 items, the last one a list. <code>dj += anu</code> would give 4 loose songs.")

add(id="L4-5", stage="L4", type="categorize", level="Read", concept="nested_mutable",
    title="Each line starts from a = 2, list_a = [1, a] and box = [3, list_a]. Does print(box) change after it?",
    items=['list_a[1] = 4', 'a = 5', 'list_a += [5]', 'list_a = [9, 9]', 'list_a = list_a + [5]'],
    categories=["box changes", "box stays [3, [1, 2]]"],
    mapping=[0, 1, 0, 1, 1],
    setup='a = 2\nlist_a = [1, a]\nbox = [3, list_a]',
    hints=["box holds the list list_a pointed at when box was made.", "Does the line change that list, or move a name?"],
    explain="box holds the list itself. Changing an index or using += changes that list, so box shows it. <code>a = 5</code>, <code>list_a = [9, 9]</code> and <code>list_a = list_a + [5]</code> only move a name; box keeps <code>[3, [1, 2]]</code>.",
    trap="Thinking <code>a = 5</code> reaches inside the list.")

# ---------- L5 · Fix Meera's App ----------
add(id="L5-2", stage="L5", type="coding", level="Extend", concept="nested_mutable",
    challenge={
        "title": "The DJ's Set List",
        "statement": "DJ Karthik keeps each friend's songs as <b>one block</b> inside set_list, so len(set_list) is the number of friends. The starter gives one long, repeated list instead. It has two mistakes: find and fix both.",
        "input_fmt": "First line: F, the number of friends. For each friend: a line with K, then K lines, one song each.",
        "output_fmt": "Two lines: print(set_list), then print(len(set_list)).",
        "starter": 'f = int(input())\nset_list = []\nblock = []\nfor i in range(f):\n    k = int(input())\n    for j in range(k):\n        block += [input()]\n    set_list += block\nprint(set_list)\nprint(len(set_list))\n',
        "tests": [
            {"stdin": "2\n2\nNaatu Naatu\nJai Ho\n1\nKesariya", "expected": "[['Naatu Naatu', 'Jai Ho'], ['Kesariya']]\n2"},
            {"stdin": "3\n1\nMalhari\n1\nJai Ho\n2\nKesariya\nNaatu Naatu", "expected": "[['Malhari'], ['Jai Ho'], ['Kesariya', 'Naatu Naatu']]\n3"},
            {"stdin": "0", "expected": "[]\n0", "hidden": True, "note": "no friends yet"},
            {"stdin": "2\n0\n1\nMalhari", "expected": "[[], ['Malhari']]\n2", "hidden": True, "note": "a friend who sends no songs"},
            {"stdin": "1\n3\nJai Ho\nJai Ho\nMalhari", "expected": "[['Jai Ho', 'Jai Ho', 'Malhari']]\n1", "hidden": True, "note": "one friend, one block"},
        ],
    },
    solution='f = int(input())\nset_list = []\nfor i in range(f):\n    k = int(input())\n    block = []\n    for j in range(k):\n        block += [input()]\n    set_list += [block]\nprint(set_list)\nprint(len(set_list))\n',
    hints=["set_list += block adds the songs one by one. How do you add the block as one item?",
           "Fixed that and every block looks the same? They are one list: make a new block = [] for each friend, inside the loop."],
    explain="<code>set_list += [block]</code> adds the block as one item. And <code>block = []</code> must be inside the loop: with one block for everyone, every item of set_list is the same list, and each friend's += changes them all.",
    trap="Fixing only the += line: then set_list holds the same block twice.")

# ---------- Final Boss ----------
add(id="B-1", stage="BOSS", type="predict", level="Read", concept="nested_mutable", scenario=True,
    title="Run the scenario on the left. What does it print?",
    options=["3 2\n['Intro', ['Butta Bomma', 'Jai Ho', 'Malhari']]", "3 2\n['Intro', ['Naatu Naatu', 'Jai Ho']]",
             "4 3\n['Intro', ['Butta Bomma', 'Jai Ho', 'Malhari']]", "3 2\n['Intro', ['Naatu Naatu', 'Jai Ho', 'Malhari']]"],
    answer=0,
    why={1: "dj holds the playlist itself, so both changes to it show inside dj.",
         2: "anu was made by + before Malhari: a separate list of 3. And += on rahul adds to the list inside dj, not to dj itself.",
         3: "Line 6 changes index 0 of the same list, so Naatu Naatu becomes Butta Bomma inside dj too."},
    hints=["Which lists does rahul += reach?", "anu was built with +. Is it the same list as playlist?"],
    explain="rahul, playlist and the second item of dj are one list: += adds Malhari and line 6 swaps index 0, and dj shows both. anu is a new list from +, made earlier, so it keeps 3 songs. dj itself still has 2 items.",
    trap="Thinking the change through rahul reaches anu.")

add(id="B-2", stage="BOSS", type="numeric", level="Read", concept="plus_equal", scenario=True,
    title="After the scenario on the left runs, what is len(rahul) + len(anu)?",
    value=6,
    hints=["rahul shares the playlist. How many songs does it have after +=?", "anu was made with + before Malhari came."],
    explain="rahul's list got Malhari through +=, so it has 3 songs. anu was a new list of 3 from the start, and nothing changed it. 3 + 3 = 6.",
    trap="Answering 7, as if anu also got Malhari.")

add(id="B-3", stage="BOSS", type="coding", level="Optimize", concept="plus_equal",
    challenge={
        "title": "One Playlist for Everyone",
        "statement": "Rahul's phone shows the playlist through the name rahul, set up before the requests came in. The starter builds a brand-new list for every request, so Rahul never sees them. Change the playlist <b>in place</b> instead, so the output works and the id check prints True. Skip every request that is just \"skip\".",
        "input_fmt": "First line: N. Then N lines, one request each.",
        "output_fmt": "Two lines: print(rahul), then print(id(rahul) == id(playlist)).",
        "starter": 'playlist = ["Naatu Naatu"]\nrahul = playlist\nn = int(input())\nfor i in range(n):\n    song = input()\n    if song != "skip":\n        playlist = playlist + [song]\nprint(rahul)\nprint(id(rahul) == id(playlist))\n',
        "tests": [
            {"stdin": "2\nJai Ho\nKesariya", "expected": "['Naatu Naatu', 'Jai Ho', 'Kesariya']\nTrue"},
            {"stdin": "3\nJai Ho\nskip\nMalhari", "expected": "['Naatu Naatu', 'Jai Ho', 'Malhari']\nTrue"},
            {"stdin": "0", "expected": "['Naatu Naatu']\nTrue", "hidden": True, "note": "no requests"},
            {"stdin": "2\nskip\nskip", "expected": "['Naatu Naatu']\nTrue", "hidden": True, "note": "every request skipped"},
            {"stdin": "1\nNaatu Naatu", "expected": "['Naatu Naatu', 'Naatu Naatu']\nTrue", "hidden": True, "note": "a song asked for twice"},
        ],
    },
    rules=[
        {"forbid": r"playlist\s*=\s*playlist\s*\+", "msg": "Don't build a new list for every request: change the playlist in place."},
        {"require": r"\+=\s*\[", "msg": "Add each song in place with += [song]."},
    ],
    solution='playlist = ["Naatu Naatu"]\nrahul = playlist\nn = int(input())\nfor i in range(n):\n    song = input()\n    if song != "skip":\n        playlist += [song]\nprint(rahul)\nprint(id(rahul) == id(playlist))\n',
    hints=["Every playlist = playlist + [song] makes a new list and leaves rahul behind.", "Which operator changes the list itself?"],
    explain="<code>playlist += [song]</code> adds to the one list in place, so no new list is made per request, rahul sees every song, and the two names keep one id.",
    trap="Adding rahul = playlist after the loop: the output passes, but a new list is still built for every request.")

add(id="B-4", stage="BOSS", type="msq", level="Prompting", concept="concat_new",
    title="You ask an AI for code that makes a backup of the playlist that stays the same when the playlist changes. Which lines must your spec include so its code is right?",
    options=["The backup must be a new list: changing playlist later must not change backup.",
             "Example: playlist = ['Jai Ho'], then playlist += ['Malhari']; print(backup) still shows ['Jai Ho'].",
             "Use only =, +, += and indexes: no list methods.",
             "It must work for an empty playlist too: the backup is then [].",
             "Make the code look professional.",
             "Write it as backup = playlist."],
    answers=[0, 1, 2, 3],
    hints=["A good spec says what must be true, gives a checkable example and the edge case, and names the tools allowed. Wishes give the AI nothing to check."],
    explain="The AI needs the rule (a new list), an example it can test, the tools your class knows, and the empty case. \"Look professional\" changes nothing, and <code>backup = playlist</code> is exactly the bug: a second name, not a backup.",
    trap="Telling the AI to write backup = playlist.")

QUESTIONS = {q["id"]: q for q in Q}
LEVEL_IDS = [lvl["id"] for lvl in LEVELS]
LEVEL_BY_ID = {lvl["id"]: lvl for lvl in LEVELS}
TOTAL = sum(len(lvl["main"]) for lvl in LEVELS)

GUIDE_HTML = """<h3>Objects and ids</h3>
    <div class="tscroll"><table><thead><tr><th>Code</th><th>Gives</th></tr></thead><tbody>
      <tr><td><code>id(playlist)</code></td><td>the object's unique id. It can be a <b>different number</b> each run, so compare ids, never memorise them</td></tr>
      <tr><td><code>id(a) == id(b)</code></td><td><code>True</code> only when a and b point at <b>one</b> object</td></tr>
      <tr><td><code>a = [1, 2]</code> and <code>b = [1, 2]</code></td><td>two lists with the same items: <b>two</b> ids</td></tr></tbody></table></div>
    <h3>What each line does · list_a = [1, 2] and list_b = list_a</h3>
    <div class="tscroll"><table><thead><tr><th>Line</th><th>What it does</th><th>list_b after it</th></tr></thead><tbody>
      <tr><td><code>list_b = list_a</code></td><td>a <b>second name</b> for the same list (same id)</td><td><code>[1, 2]</code></td></tr>
      <tr><td><code>list_a[1] = 6</code></td><td>changes an item of the shared list</td><td><code>[1, 6]</code></td></tr>
      <tr><td><code>list_a += [6, 7]</code></td><td>changes the shared list <b>in place</b></td><td><code>[1, 2, 6, 7]</code></td></tr>
      <tr><td><code>list_a = list_a + [6, 7]</code></td><td><code>+</code> makes a <b>new</b> list; only list_a moves to it</td><td><code>[1, 2]</code></td></tr>
      <tr><td><code>list_a = [6, 7]</code></td><td>points list_a at a <b>new</b> list</td><td><code>[1, 2]</code></td></tr></tbody></table></div>
    <h3>Lists inside lists</h3>
    <div class="tscroll"><table><thead><tr><th>Code</th><th>Result</th></tr></thead><tbody>
      <tr><td><code>list_b = [3, list_a]</code>, then <code>list_a[1] = 4</code></td><td><code>[3, [1, 4]]</code>: list_b holds the list itself</td></tr>
      <tr><td><code>a = 2</code>, <code>list_a = [1, a]</code>, then <code>a = 3</code></td><td><code>[1, 2]</code>: numbers and strings never change in place</td></tr>
      <tr><td><code>animals += wild_animals</code></td><td>adds each item: <code>['cat', 'dog', 'Tiger', 'Fox']</code></td></tr>
      <tr><td><code>animals += [wild_animals]</code></td><td>adds the list as <b>one</b> item: <code>['cat', 'dog', ['Tiger', 'Fox']]</code></td></tr></tbody></table></div>
    <h3>Remember</h3>
    <ul><li>Ask of every line: does it <b>change</b> a list (index, <code>+=</code>), or <b>point a name</b> at a list (<code>=</code>)?</li>
      <li>A change to a list shows through <b>every</b> name for it, and inside every list that holds it.</li>
      <li>Need a real backup? <code>backup = playlist + []</code> makes a new list with the same items.</li>
      <li>Changing an index that does not exist, like <code>playlist[3]</code> in a 3-item list, stops with <b>IndexError</b>.</li></ul>"""

LAB_STARTER = '''list_a = [1, 2]
list_b = list_a
print(id(list_a) == id(list_b))
list_a += [6, 7]
print("list b : " + str(list_b))
list_a = list_a + [8]
print("list b : " + str(list_b))
print(id(list_a) == id(list_b))
'''

UI = {
    "id": "wlists",
    "title": "Working with Lists: The Python Challenge",
    "short": "Working with Lists",
    "hero_h1": "Mission: <em>Save the Fresher's Night Playlist</em>",
    "hero_p": "Meera is the class rep, and Fresher's Night is on Friday. She made one playlist and shared it with her friends. Now songs change by themselves, Rahul's backup is no backup, and the DJ's list is a mess. Help her fix it, one stage at a time.",
    "story": """<p><b>Meera is the class rep, and Fresher's Night is on Friday.</b> She made one playlist and shared it. Now it's a mess: songs change by themselves, Rahul's "backup" keeps changing, and DJ Karthik's request list shows songs nobody added.</p>
      <h3>Your 3 jobs</h3>
      <ol><li>🔍 <b>Find who shares the playlist.</b> Rahul and Anu both say they have it. Use id() to check.</li>
        <li>➕ <b>Add songs the right way.</b> Some ways reach everyone, some make a new list. Know which is which.</li>
        <li>🎧 <b>Fix the DJ's set list.</b> Keep each friend's songs as one block, inside one list.</li></ol>
      <p class="win">You win when every stage is cleared and Fresher's Night is saved.</p>""",
    "lab": "py",
    "lab_name": "List Lab",
    "lab_starter": LAB_STARTER,
    "lab_tips": [
        'Run it first. Why does the first line print <code>True</code>?',
        'Change <code>list_b = list_a</code> to <code>list_b = list_a + []</code>. Which lines change, and why?',
        'Swap <code>list_a += [6, 7]</code> for <code>list_a = list_a + [6, 7]</code>. Does <code>list_b</code> still see 6 and 7?',
        'Add <code>outer = [3, list_a]</code>, then <code>list_a[0] = 9</code>. Print <code>outer</code>.',
        'Make <code>a = 2</code> and <code>nums = [1, a]</code>, then set <code>a = 3</code>. Does <code>nums</code> change?',
    ],
    "boss_win": "Fresher's Night saved!",
    "champion": "Working with Lists Champion",
    "guide_title": "Field guide: working with lists",
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
    ("lab", "🧪", "The List Lab"),
    ("debug", "🐞", "Debugging missions"),
    ("coding", "💻", "Coding challenges"),
    ("hints", "💡", "Hints and explanations"),
    ("xp", "🏆", "XP and badges"),
]

FEEDBACK_TOPIC = "working with lists"
