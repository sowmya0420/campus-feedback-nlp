import re

p = "src/aspects.py"
s = open(p, encoding="utf-8").read()

def add(fac, cat, words):
    """Append words to a LEXICON[fac][cat] list."""
    global s
    pat = re.compile(r'(\n    "%s": \{.*?\n        "%s": \[)(.*?)(\],)' % (fac, re.escape(cat)), re.S)
    m = pat.search(s)
    assert m, (fac, cat)
    extra = ", ".join('"%s"' % w for w in words)
    s = s[:m.end(2)] + ", " + extra + s[m.end(2):]

def remove(fac, cat, words):
    """Remove words from a LEXICON[fac][cat] list."""
    global s
    pat = re.compile(r'(\n    "%s": \{.*?\n        "%s": \[)(.*?)(\],)' % (fac, re.escape(cat)), re.S)
    m = pat.search(s)
    assert m, (fac, cat)
    body = m.group(2)
    for w in words:
        body = body.replace('"%s", ' % w, "").replace(', "%s"' % w, "").replace('"%s"' % w, "")
    s = s[:m.start(2)] + body + s[m.end(2):]

# --- Recall: add missing keywords ---
add("canteen", "food quality", ["kulfi", "falooda", "juice", "sandwich", "pizza", "burger", "noodles", "fries", "ice cream", "shake", "parotta", "chaat", "pani puri", "vada", "bajji", "bonda"])
add("hostel_mess", "price", ["overpriced", "extras", "extra charge", "omelette", "milk"])
add("hostel_mess", "seating", ["dining area", "dining hall", "spacious"])
add("hostel_mess", "quantity", ["finish early", "finishes early", "finished early", "nothing left", "latecomers", "not enough"])
add("hostel_mess", "hygiene", ["sticky", "nobody cleans"])
add("wifi", "bandwidth limit", ["data", "mudinjiduchu", "mudinjidum", "mudinjathu", "finished"])
add("wifi", "coverage", ["not available", "no wifi", "cafeteria", "canteen", "classroom", "classrooms", "ground", "auditorium"])
add("library", "cleanliness", ["graffiti", "scratches", "scratched", "stains", "stained", "writing on"])
add("hostel_rooms", "maintenance", ["loose", "torn", "mesh", "hinge", "hinges", "latch", "reported", "no response"])
add("transport", "safety", ["speed limit", "adheres", "highway", "helmet", "lights"])
add("transport", "driver behavior", ["drives smoothly", "drives"])
add("classrooms", "noise", ["rattling", "rattle", "rattles"])

# --- Precision: remove over-triggering words ---
remove("wifi", "connectivity", ["wifi", "wi-fi", "network", "net"])
remove("classrooms", "ac/temperature", ["fan", "fans"])
add("classrooms", "ac/temperature", ["ceiling fan not working", "fan speed", "no fan"])
remove("library", "book availability", ["issue", "available", "reference"])
remove("wifi", "coverage", ["hostel", "library"])
remove("hostel_mess", "variety", ["same"])
add("hostel_mess", "variety", ["same food", "same items", "same every day"])
remove("hostel_mess", "quantity", ["less"])
remove("canteen", "quantity", ["less"])
remove("hostel_mess", "food quality", ["boiled"])
remove("hostel_rooms", "cleanliness", ["smell"])
remove("hostel_rooms", "room size", ["sharing", "space", "size"])
remove("hostel_rooms", "electricity", ["light", "lights"])
remove("library", "seating", ["full", "space"])
remove("library", "book availability", ["outdated"])

open(p, "w", encoding="utf-8").write(s)
print("patched")