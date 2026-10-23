import re

p = "src/aspects.py"
s = open(p, encoding="utf-8").read()

def _find(fac, cat):
    pat = re.compile(r'(\n    "%s": \{.*?\n        "%s": \[)(.*?)(\],)' % (fac, re.escape(cat)), re.S)
    m = pat.search(s)
    assert m, (fac, cat)
    return m

def add(fac, cat, words):
    global s
    m = _find(fac, cat)
    extra = ", ".join('"%s"' % w for w in words)
    s = s[:m.end(2)] + ", " + extra + s[m.end(2):]

def remove(fac, cat, words):
    global s
    m = _find(fac, cat)
    body = m.group(2)
    for w in words:
        body = body.replace('"%s", ' % w, "").replace(', "%s"' % w, "").replace('"%s"' % w, "")
    s = s[:m.start(2)] + body + s[m.end(2):]

# Precision: generic nouns that trigger the wrong category
remove("hostel_mess", "seating", ["tables"])
remove("hostel_mess", "food quality", ["dinner", "lunch", "breakfast"])
remove("library", "seating", ["desk", "desks"])
remove("classrooms", "seating", ["bench", "benches", "desk", "desks"])
remove("hostel_rooms", "cleanliness", ["mosquito", "mosquitoes"])
remove("transport", "bus condition", ["bus", "buses"])
remove("transport", "crowding", ["standing", "stand"])

# Recall: typos, slang, missing words
add("hostel_rooms", "cleanliness", ["cleaning", "cleans", "cleaned"])
add("transport", "driver behavior", ["rashly", "sharp turn"])
add("transport", "safety", ["tumble", "fell", "fall"])
add("transport", "punctuality", ["gps", "tracking", "location", "app"])
add("wifi", "login issues", ["helpdesk", "help desk", "picks up", "it team"])
add("library", "digital resources", ["digitl", "digtal", "resources"])
add("labs", "equipment condition", ["routers", "switches", "network lab"])
add("canteen", "waiting time", ["upi", "payment", "cash"])

open(p, "w", encoding="utf-8").write(s)
print("patched")