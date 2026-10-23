import re
from src.preprocess import split_clauses

# facility -> category -> keywords (English, Tanglish, common typos)
LEXICON = {
    "canteen": {
        "food quality": ["food", "taste", "tasty", "dosa", "idli", "biryani", "rice", "meals", "tea", "coffee", "snacks", "oily", "stale", "fresh", "samosa", "puff", "saapadu", "sapadu", "unavu", "kulfi", "falooda", "juice", "sandwich", "pizza", "burger", "noodles", "fries", "ice cream", "shake", "parotta", "chaat", "pani puri", "vada", "bajji", "bonda"],
        "price": ["price", "prices", "rupees", "rs", "costly", "expensive", "cheap", "overpriced", "rate", "cost", "kaasu"],
        "hygiene": ["hygiene", "hygienic", "clean", "dirty", "unclean", "cockroach", "flies", "unhygienic", "washing"],
        "waiting time": ["wait", "waiting", "queue", "line", "late", "slow", "delay", "long time", "upi", "payment", "cash"],
        "seating": ["seat", "seating", "seats", "chairs", "tables", "place to sit", "crowded"],
        "staff behavior": ["staff", "server", "servers", "cashier", "behaviour", "behavior", "rude", "polite", "uncle", "akka", "anna"],
        "quantity": ["quantity", "portion", "portions", "serving", "servings", "small"],
        "variety": ["variety", "options", "menu", "same items", "choices", "repeat"],
    },
    "hostel_mess": {
        "food quality": ["food", "taste", "tasty", "rice", "sambar", "curry", "chapati", "roti", "dal", "meals", "stale", "oily", "undercooked", "saapadu", "sapadu", "unavu", "kuzhambu", "rasam"],
        "waiting time": ["wait", "waiting", "queue", "line", "late", "delay", "timing", "timings"],
        "hygiene": ["hygiene", "hygienic", "clean", "dirty", "unclean", "insects", "hair", "worm", "worms", "cockroach", "flies", "plates", "unhygienic", "sticky", "nobody cleans"],
        "quantity": ["quantity", "portion", "portions", "serving", "servings", "small", "run out", "runs out", "ran out", "finish early", "finishes early", "finished early", "nothing left", "latecomers", "not enough"],
        "variety": ["variety", "options", "menu", "repeat", "monotonous", "boring", "same food", "same items", "same every day"],
        "price": ["price", "fee", "fees", "charges", "mess bill", "bill", "cost", "expensive", "costly", "overpriced", "extras", "extra charge", "omelette", "milk"],
        "staff behavior": ["staff", "server", "servers", "cook", "cooks", "warden", "behaviour", "behavior", "rude", "polite", "manager"],
        "seating": ["seat", "seating", "seats", "chairs", "crowded", "place to sit", "dining area", "dining hall", "spacious"],
    },
    "classrooms": {
        "projector/av": ["projector", "projection", "screen", "mic", "microphone", "speaker", "speakers", "audio", "sound system", "av", "display", "hdmi", "smartboard", "smart board"],
        "ac/temperature": ["ac", "a/c", "air conditioner", "air conditioning", "hot", "cold", "temperature", "ventilation", "stuffy", "sweating", "cooling", "ceiling fan not working", "fan speed", "no fan"],
        "noise": ["noise", "noisy", "loud", "echo", "disturbance", "sound", "construction", "rattling", "rattle", "rattles"],
        "cleanliness": ["clean", "dirty", "dust", "dusty", "cleanliness", "board", "whiteboard", "blackboard", "trash", "dustbin", "garbage", "litter", "unclean"],
        "lighting": ["light", "lights", "lighting", "tube", "tubes", "bulb", "bulbs", "dark", "dim", "bright", "lamp"],
        "seating": ["seat", "seating", "seats", "chair", "chairs", "uncomfortable", "broken", "crowded", "space"],
    },
    "hostel_rooms": {
        "cleanliness": ["clean", "dirty", "dust", "dusty", "cleanliness", "bathroom", "toilet", "toilets", "washroom", "washrooms", "sweeping", "cockroach", "cockroaches", "bedbugs", "unclean", "housekeeping", "cleaning", "cleans", "cleaned"],
        "safety": ["safe", "safety", "security", "lock", "locks", "theft", "stolen", "cctv", "guard", "guards", "unsafe", "door", "fire"],
        "room size": ["room size", "small", "cramped", "spacious", "tiny", "congested", "cot", "cupboard", "storage"],
        "maintenance": ["maintenance", "repair", "repairs", "broken", "fix", "fixed", "leak", "leaking", "leakage", "complaint", "complaints", "damaged", "plumber", "carpenter", "window", "windows", "fan", "fans", "loose", "torn", "mesh", "hinge", "hinges", "latch", "reported", "no response"],
        "water supply": ["water", "thanni", "tap", "taps", "geyser", "hot water", "supply", "shower", "bucket", "tank"],
        "electricity": ["electricity", "current", "power", "power cut", "power cuts", "outage", "socket", "sockets", "plug", "plugs", "voltage", "charging", "wiring", "switch", "switches"],
        "noise": ["noise", "noisy", "loud", "music", "disturbance", "disturb", "shouting", "silence", "quiet"],
        "laundry": ["laundry", "washing machine", "washing machines", "clothes", "dryer", "drying", "iron", "ironing", "dhobi"],
    },
    "labs": {
        "equipment condition": ["equipment", "equipments", "instrument", "instruments", "apparatus", "machine", "machines", "broken", "faulty", "damaged", "outdated", "old", "oscilloscope", "components", "kits", "kit", "condition", "not working", "defective", "routers", "switches", "network lab"],
        "lab staff": ["staff", "technician", "technicians", "assistant", "assistants", "instructor", "lab in-charge", "incharge", "in-charge", "faculty", "helpful", "rude", "support", "behaviour", "behavior"],
        "lab timings": ["timing", "timings", "hours", "schedule", "slot", "slots", "closed", "open", "access", "after class", "extend", "extended", "late", "time"],
        "cleanliness": ["clean", "dirty", "dust", "dusty", "cleanliness", "mess", "messy", "unclean", "trash", "garbage"],
        "system speed": ["system", "systems", "computer", "computers", "pc", "pcs", "slow", "lag", "lagging", "hang", "hangs", "hanging", "speed", "processor", "ram", "freeze", "freezes", "boot", "loading"],
        "software availability": ["software", "license", "licence", "licenses", "licences", "matlab", "install", "installed", "installation", "ide", "compiler", "tools", "version", "tool", "packages", "ansys", "autocad"],
        "space": ["space", "crowded", "cramped", "small", "spacious", "seating", "congested", "room", "batch", "batches", "workstation", "workstations"],
    },
    "library": {
        "staff behavior": ["staff", "librarian", "librarians", "behaviour", "behavior", "rude", "polite", "helpful", "attitude", "counter", "assistant"],
        "book availability": ["book", "books", "copies", "copy", "textbook", "textbooks", "stock", "availability", "collection", "journals", "edition", "editions", "issued"],
        "silence": ["silence", "silent", "quiet", "noise", "noisy", "loud", "talking", "whispering", "peaceful", "disturbance", "chatting"],
        "opening hours": ["hours", "timing", "timings", "open", "opens", "closed", "closes", "closing", "opening", "late", "midnight", "weekend", "weekends", "sunday", "exam time"],
        "digital resources": ["digital", "e-book", "ebook", "ebooks", "e-books", "online", "database", "databases", "ieee", "journal access", "e-resources", "portal", "nptel", "scopus", "subscription", "pdf", "digitl", "digtal", "resources"],
        "seating": ["seat", "seating", "seats", "chairs", "tables", "crowded", "sit", "reading room"],
        "cleanliness": ["clean", "dirty", "dust", "dusty", "cleanliness", "unclean", "washroom", "washrooms", "smell", "graffiti", "scratches", "scratched", "stains", "stained", "writing on"],
        "ac/temperature": ["ac", "a/c", "air conditioner", "air conditioning", "fan", "fans", "hot", "cold", "temperature", "stuffy", "ventilation", "cooling", "freezing"],
    },
    "transport": {
        "driver behavior": ["driver", "drivers", "driving", "rash", "rude", "behaviour", "behavior", "conductor", "speeding", "polite", "attitude", "shouting", "drives smoothly", "drives", "rashly", "sharp turn"],
        "punctuality": ["late", "delay", "delayed", "punctual", "punctuality", "time", "timing", "timings", "waiting", "on time", "wait", "schedule", "early", "arrives", "arrive", "gps", "tracking", "location", "app"],
        "bus condition": ["seat", "seats", "condition", "broken", "old", "dirty", "clean", "maintenance", "breakdown", "breakdowns", "windows", "ac", "tyre", "tyres", "leaking", "vehicle"],
        "fare": ["fare", "fares", "fee", "fees", "charges", "price", "cost", "expensive", "costly", "pass", "ticket", "hike", "amount", "rupees"],
        "route coverage": ["route", "routes", "coverage", "stop", "stops", "pickup", "pick-up", "pickup point", "area", "areas", "cover", "covers", "covered", "pick up", "drop", "drops"],
        "safety": ["safe", "safety", "unsafe", "security", "accident", "accidents", "night", "girls", "women", "emergency", "cctv", "seatbelt", "seatbelts", "overspeeding", "dangerous", "speed limit", "adheres", "highway", "helmet", "lights", "tumble", "fell", "fall"],
        "crowding": ["crowd", "crowded", "crowding", "overcrowded", "packed", "jam", "jammed", "capacity", "full", "squeeze", "squeezed"],
    },
    "wifi": {
        "speed": ["speed", "slow", "fast", "buffering", "lag", "lagging", "download", "upload", "mbps", "loading", "ping", "latency", "internet"],
        "coverage": ["coverage", "signal", "range", "block", "blocks", "corner", "corners", "floor", "floors", "dead zone", "dead zones", "weak", "available", "reach", "reaches", "not available", "no wifi", "cafeteria", "canteen", "classroom", "classrooms", "ground", "auditorium"],
        "login issues": ["login", "log in", "logging", "password", "otp", "authentication", "portal", "credentials", "captive", "sign in", "username", "register", "registration", "logout", "logged out", "helpdesk", "help desk", "picks up", "it team"],
        "reliability": ["reliable", "reliability", "disconnect", "disconnects", "disconnected", "drops", "dropping", "unstable", "stable", "stability", "down", "outage", "outages", "keeps", "cuts", "cut"],
        "bandwidth limit": ["bandwidth", "limit", "limits", "quota", "data cap", "capped", "throttle", "throttled", "throttling", "restriction", "restrictions", "blocked", "block", "youtube", "streaming", "gb", "daily limit", "data", "mudinjiduchu", "mudinjidum", "mudinjathu", "finished"],
        "connectivity": ["connect", "connection", "connectivity", "connected", "access point", "access points", "router", "routers", "no internet"],
    },
}

# Compile once: whole-word match, optional plural s/es
_PATTERNS = {}
for fac, cats in LEXICON.items():
    _PATTERNS[fac] = {
        cat: [(kw, re.compile(r"\b" + re.escape(kw) + r"(?:s|es)?\b"))
              for kw in sorted(set(kws), key=len, reverse=True)]
        for cat, kws in cats.items()
    }


def extract_aspects(text, facility):
    """Return [{aspect_term, category, clause}] for one comment.
    One aspect per (clause, category). Falls back to 'general' if nothing matches."""
    pats = _PATTERNS.get(facility, {})
    results, seen = [], set()
    clauses = split_clauses(text)
    for clause in clauses:
        for cat, plist in pats.items():
            for kw, rx in plist:
                m = rx.search(clause)
                if m:
                    if (clause, cat) not in seen:
                        seen.add((clause, cat))
                        results.append({"aspect_term": m.group(0), "category": cat, "clause": clause})
                    break
    if not results:
        whole = " ".join(clauses)
        results.append({"aspect_term": None, "category": "general", "clause": whole})
    return results