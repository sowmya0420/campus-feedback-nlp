"""Modules 4 + 5. Reads predictions.csv -> ratings.csv, issues.csv. Non-abusive comments only.
Rating = 1 + 4*(pos + 0.5*neutral)/n   (range 1..5)"""
import pandas as pd
from src import config

def rating(g):
    n = len(g)
    return round(1 + 4 * ((g.sentiment == "positive").sum() + 0.5 * (g.sentiment == "neutral").sum()) / n, 2)

def run(pred_path="data/outputs/predictions.csv"):
    d = pd.read_csv(pred_path)
    d = d[(~d["abusive"]) & (d["category"] != "general")]
    rows = []
    for (fac, cat), g in d.groupby(["facility", "category"]):
        rows.append({"facility": fac, "category": cat, "mentions": len(g), "rating": rating(g),
                     "positive": (g.sentiment == "positive").sum(), "neutral": (g.sentiment == "neutral").sum(),
                     "negative": (g.sentiment == "negative").sum(),
                     "negative_share": round((g.sentiment == "negative").mean(), 3)})
    asp = pd.DataFrame(rows)
    fac = d.groupby("facility").apply(rating, include_groups=False).rename("rating").reset_index()
    fac["category"] = "OVERALL"
    fac["mentions"] = d.groupby("facility").size().values
    ratings = pd.concat([fac, asp], ignore_index=True)
    ratings.to_csv("data/outputs/ratings.csv", index=False)
    issues = asp[(asp.negative_share >= config.ISSUE_NEG_SHARE) & (asp.mentions >= config.ISSUE_MIN_MENTIONS)]
    issues = issues.sort_values(["facility", "negative_share"], ascending=[True, False])
    issues.to_csv("data/outputs/issues.csv", index=False)
    print(f"ratings.csv: {len(ratings)} rows | issues.csv: {len(issues)} recurring issues")

if __name__ == "__main__":
    run()
