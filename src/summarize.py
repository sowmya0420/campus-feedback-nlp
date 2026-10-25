"""Module 6: summary per facility. Uses Ollama (local AI) to write the summary
from the facts; checks the AI text against the facts; falls back to the old
template if Ollama is not available or keeps getting it wrong.
-> data/outputs/summaries.csv"""
import re
import pandas as pd
from src.summarize_ai import summarize_with_ollama

def top_aspects(r):
    a = r[(r.category != "OVERALL") & (r.mentions >= 3)]
    neg = a.sort_values(["negative_share", "mentions"], ascending=False).head(3)
    pos = a.sort_values(["negative_share", "mentions"], ascending=[True, False]).head(2)
    return neg, pos

def summary(fac, r):
    """Old template summary (kept as the backup)."""
    overall = r[r.category == "OVERALL"].iloc[0]
    name = fac.replace("_", " ")
    neg, pos = top_aspects(r)
    s = f"Students rate the {name} {overall.rating}/5 overall based on {int(overall.mentions)} aspect mentions. "
    if len(neg):
        s += "Main concerns: " + ", ".join(f"{x.category} ({x.negative_share:.0%} negative)" for x in neg.itertuples()) + ". "
    if len(pos):
        s += "Best-liked: " + ", ".join(f"{x.category} ({1 - x.negative_share:.0%} not negative)" for x in pos.itertuples()) + "."
    return s

def facts_text(fac, r):
    """The same numbers, written as plain facts for the AI to read."""
    overall = r[r.category == "OVERALL"].iloc[0]
    neg, pos = top_aspects(r)
    lines = [f"Overall rating: {overall.rating} out of 5, from {int(overall.mentions)} aspect mentions in student comments."]
    if len(neg):
        lines.append("Biggest concerns:")
        lines += [f"- {x.category}: {x.negative_share:.0%} of {int(x.mentions)} mentions were negative" for x in neg.itertuples()]
    low = pos[pos.negative_share < 0.40]
    mid = pos[pos.negative_share >= 0.40]
    if len(low):
        lines.append("Areas with few complaints (under 40% negative):")
        lines += [f"- {x.category}: {x.negative_share:.0%} of {int(x.mentions)} mentions were negative" for x in low.itertuples()]
    if len(mid):
        lines.append("Less negative than the other areas, but still often criticised (40% or more negative):")
        lines += [f"- {x.category}: {x.negative_share:.0%} of {int(x.mentions)} mentions were negative" for x in mid.itertuples()]
    return "\n".join(lines)

def looks_wrong(text, facts, all_cats):
    """Returns a list of problems found in the AI text (empty list = fine)."""
    problems = []
    for p in re.findall(r"\d+%", text):
        if p not in facts:
            problems.append(f"number {p} is not in the facts")
    if "few complaints" in text.lower() and "Areas with few complaints" not in facts:
        problems.append('says "few complaints" but no area qualifies')
    for c in all_cats:
        if re.search(r"\b" + re.escape(c.lower()) + r"\b", text.lower()) and c.lower() not in facts.lower():
            problems.append(f"mentions {c}, which is not in the facts")
    return problems

def run():
    r = pd.read_csv("data/outputs/ratings.csv")
    all_cats = [c for c in r.category.unique() if c != "OVERALL"]
    rows = []
    for fac, g in r.groupby("facility"):
        name = fac.replace("_", " ")
        facts = facts_text(fac, g)
        text, method = None, "template"
        for attempt in range(3):
            try:
                t = summarize_with_ollama(name, facts)
            except Exception as e:
                print(f"  {fac}: Ollama problem ({e})")
                break
            bad = looks_wrong(t, facts, all_cats) if t else ["empty reply"]
            if not bad:
                text, method = t, "ai"
                break
            print(f"  {fac}: try {attempt + 1} rejected: {bad}")
        if text is None:
            text = summary(fac, g)
        print(f"done: {fac} ({method})")
        rows.append({"facility": fac, "summary": text, "method": method})
    out = pd.DataFrame(rows)
    out.to_csv("data/outputs/summaries.csv", index=False)
    print(out[["facility", "method"]].to_string(index=False))

if __name__ == "__main__":
    run()