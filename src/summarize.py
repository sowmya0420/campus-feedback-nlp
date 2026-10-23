"""Module 6 baseline: template summary per facility from top negative / positive aspects.
(Upgrade later: pass the same facts to an LLM/BART.)  -> data/outputs/summaries.csv"""
import pandas as pd

def summary(fac, r):
    a = r[r.category != "OVERALL"]
    overall = r[r.category == "OVERALL"].iloc[0]
    name = fac.replace("_", " ")
    neg = a[a.mentions >= 3].sort_values(["negative_share", "mentions"], ascending=False).head(3)
    pos = a[a.mentions >= 3].sort_values(["negative_share", "mentions"], ascending=[True, False]).head(2)
    s = f"Students rate the {name} {overall.rating}/5 overall based on {int(overall.mentions)} aspect mentions. "
    if len(neg):
        s += "Main concerns: " + ", ".join(f"{x.category} ({x.negative_share:.0%} negative)" for x in neg.itertuples()) + ". "
    if len(pos):
        s += "Best-liked: " + ", ".join(f"{x.category} ({1 - x.negative_share:.0%} not negative)" for x in pos.itertuples()) + "."
    return s

def run():
    r = pd.read_csv("data/outputs/ratings.csv")
    out = pd.DataFrame([{"facility": f, "summary": summary(f, g)} for f, g in r.groupby("facility")])
    out.to_csv("data/outputs/summaries.csv", index=False)
    print(out.to_string(index=False, max_colwidth=160))

if __name__ == "__main__":
    run()
