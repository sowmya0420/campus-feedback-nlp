"""Module 6: facility summaries.

Reads data/outputs/ratings.csv (made by src.aggregate) and writes one short, readable paragraph
per facility to data/outputs/summaries.csv (columns: facility, summary).

Two ways to write the paragraph:
  "template" - fixed sentence patterns filled in with the real numbers. Works offline and is always correct.
  "claude"   - an AI language model (Claude) writes the paragraph from the same facts.
               Needs an API key in the environment variable ANTHROPIC_API_KEY.
Every AI paragraph is checked against the facts (right rating, every main problem named, no invented
numbers, good aspects not described as problems, not just a copy of the facts). If a paragraph fails
the check, or the AI call fails, the template paragraph is used for that facility instead.

Run from the project folder:   python -m src.summarize_ai
"""
import os
import re
import pandas as pd

BACKEND = "claude" if os.environ.get("ANTHROPIC_API_KEY") else "template"
CLAUDE_MODEL = "claude-haiku-5-5"
PROBLEM_MIN_NEG = 0.5      # an aspect counts as a "problem" if at least half its mentions are negative
DISPLAY = {"wifi": "campus Wi-Fi", "transport": "college transport"}   # nicer names in sentences
POSITIVE_CUES = re.compile(r"\b(best|better|relatively|least|well|positive|strength|liked|good|bright)\b", re.I)


def pct(x):
    return f"{round(float(x) * 100)}%"


def join_words(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def facts(g):
    a = g[g.category != "OVERALL"]
    overall = g[g.category == "OVERALL"].iloc[0]
    cand = a[a.mentions >= 3]
    neg = cand.sort_values(["negative_share", "mentions"], ascending=False).head(3)
    neg = neg[neg.negative_share >= PROBLEM_MIN_NEG]
    pos = cand.sort_values(["negative_share", "mentions"], ascending=[True, False]).head(2)
    pos = pos[~pos.category.isin(neg.category)]
    return overall, neg, pos


def readable_summary(fac, overall, neg, pos):
    name = DISPLAY.get(fac, fac.replace("_", " "))
    r = float(overall.rating)
    if r < 2.0:
        mood = "mostly dissatisfied with"
    elif r < 2.75:
        mood = "more critical than positive about"
    elif r < 3.25:
        mood = "divided about"
    elif r < 4.0:
        mood = "fairly satisfied with"
    else:
        mood = "very satisfied with"
    s = [f"Students are {mood} the {name}, which is rated {overall.rating} out of 5 from {int(overall.mentions)} mentions."]
    if len(neg):
        s.append("The biggest problems are " + join_words(
            [f"{x.category} ({pct(x.negative_share)} negative)" for x in neg.itertuples()]) + ".")
    else:
        s.append("No aspect has mostly negative feedback.")
    if len(pos):
        s.append("Relatively better received: " + join_words(
            [f"{x.category} ({pct(1 - x.negative_share)} not negative)" for x in pos.itertuples()]) + ".")
    return " ".join(s)


INSTRUCTION = (
    "You are writing one short paragraph for a college facility manager, using only the facts below. "
    "Write 2 or 3 plain sentences. Mention the overall rating, the biggest problems with their percentages, "
    "and the aspects that are relatively better received. Do not use any number or aspect name that is not "
    "in the facts. No bullet points, no bold text, no headings.\n\nFACTS\n")


def facts_block(fac, overall, neg, pos):
    lines = [f"Facility: {fac.replace('_', ' ')}",
             f"Overall rating: {overall.rating} out of 5 from {int(overall.mentions)} student mentions"]
    if len(neg):
        lines.append("Biggest problems (share of mentions that were negative): " + "; ".join(
            f"{x.category} {pct(x.negative_share)}" for x in neg.itertuples()))
    if len(pos):
        lines.append("Relatively better received (share of mentions that were not negative): " + "; ".join(
            f"{x.category} {pct(1 - x.negative_share)}" for x in pos.itertuples()))
    return "\n".join(lines)


def clean(text):
    text = re.sub(r"[*#`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def trigrams(text):
    w = re.findall(r"[a-z0-9.%]+", text.lower())
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)}


def check(text, facts_text, overall, neg, pos):
    """Return None if the AI paragraph matches the facts, otherwise the reason it failed."""
    if not 20 <= len(text.split()) <= 90:
        return "wrong length"
    low = text.lower()
    if "overall rating:" in low or "biggest problems (" in low:
        return "copied the facts"
    t3 = trigrams(text)
    if t3 and len(t3 & trigrams(facts_text)) / len(t3) > 0.6:
        return "copied the facts"
    if str(overall.rating) not in text:
        return "rating missing"
    for c in neg.category:
        if c.lower() not in low:
            return f"problem '{c}' missing"
    allowed = set(re.findall(r"\d+(?:\.\d+)?", facts_text)) | {"5"}
    if any(n not in allowed for n in re.findall(r"\d+(?:\.\d+)?", text)):
        return "number not in the facts"
    for sent in re.split(r"(?<=[.!?])\s+", text):
        s = sent.lower()
        if (any(c.lower() in s for c in pos.category) and not any(c.lower() in s for c in neg.category)
                and not POSITIVE_CUES.search(s)):
            return "good aspect described as a problem"
    return None


def claude_generate(prompt):
    import requests
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": CLAUDE_MODEL, "max_tokens": 250, "temperature": 0,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=60)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def run(ratings_path="data/outputs/ratings.csv", out="data/outputs/summaries.csv",
        source_out="data/outputs/summaries_source.csv", backend=None, generate=None):
    backend = backend or BACKEND
    generate = generate or claude_generate
    r = pd.read_csv(ratings_path)
    rows, meta = [], []
    for fac, g in r.groupby("facility"):
        overall, neg, pos = facts(g)
        text, source, reason = readable_summary(fac, overall, neg, pos), "template", ""
        if backend == "claude":
            block = facts_block(fac, overall, neg, pos)
            try:
                ai = clean(generate(INSTRUCTION + block))
                reason = check(ai, block, overall, neg, pos) or ""
                if not reason:
                    text, source = ai, "ai"
            except Exception as e:
                reason = f"AI call failed: {type(e).__name__}"
        rows.append({"facility": fac, "summary": text})
        meta.append({"facility": fac, "source": source, "reason": reason})
    pd.DataFrame(rows).to_csv(out, index=False)
    pd.DataFrame(meta).to_csv(source_out, index=False)
    for x in rows:
        print(f"\n{x['facility']}\n  {x['summary']}")
    n_ai = sum(m["source"] == "ai" for m in meta)
    print(f"\nBackend: {backend}. {n_ai} of {len(meta)} summaries written by the AI model; "
          f"{len(meta) - n_ai} use the template (details in {source_out}).")


if __name__ == "__main__":
    run()