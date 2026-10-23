import re

# Words that start a new clause (English + Tanglish)
CONTRAST = r"\b(?:but|however|though|although|yet|aana|aanaal|anaal)\b"
# Split on ; , ! ? and on periods (but not decimals like 2.5)
PUNCT = r"[;,!?]+|(?<!\d)\.|\.(?!\d)"


def clean_text(text):
    """Lowercase, normalise quotes, shorten stretched letters, tidy spaces."""
    text = str(text).lower()
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)   # soooo -> soo
    return re.sub(r"\s+", " ", text).strip()


def split_clauses(text):
    """Split a comment into clauses at punctuation and contrast words."""
    text = clean_text(text)
    parts = re.split(f"{PUNCT}|{CONTRAST}", text)
    return [p.strip() for p in parts if p and p.strip()]


def tokenize(clause):
    return re.findall(r"[a-z0-9']+", clause)


def clause_with_term(text, term):
    """Return the clause containing the aspect term; whole text if not found."""
    if not term:
        return clean_text(text)
    term = clean_text(term)
    for c in split_clauses(text):
        if term in c:
            return c
    return clean_text(text)