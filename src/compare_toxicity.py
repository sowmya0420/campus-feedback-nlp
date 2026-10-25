"""Module 7: baseline (TF-IDF + LogisticRegression) vs unitary/toxic-bert,
scored on the same comments. Reuses the saved toxic-bert scores, so it runs in seconds.
Run: python -m src.compare_toxicity"""
import joblib
import pandas as pd

CUT = 0.5  # score at or above this = flagged as abusive

def to_bool(s):
    return s.astype(str).str.strip().str.lower().isin(["true", "1", "1.0", "yes"]).values

def row(name, y, flag):
    tp = int((flag & y).sum())
    fp = int((flag & ~y).sum())
    fn = int((~flag & y).sum())
    p = tp / (tp + fp) if tp + fp else 0
    r = tp / (tp + fn) if tp + fn else 0
    f = 2 * p * r / (p + r) if p + r else 0
    print(f"  {name:26s} caught {tp:4d}/{tp + fn:<4d} false alarms {fp:4d} | "
          f"precision {p:.0%}  recall {r:.0%}  F1 {f:.2f}")

def table(title, y, base, bert):
    print(f"\n{title}  ({int(y.sum())} abusive out of {len(y)})")
    row("baseline alone", y, base)
    row("toxic-bert alone", y, bert)
    row("either one flags", y, base | bert)
    row("both must flag", y, base & bert)

def main():
    try:
        model = joblib.load("models/toxicity_tfidf_logreg.joblib")
    except FileNotFoundError:
        raise SystemExit("Baseline model not found. Run: python -m src.toxicity_baseline")

    camp = pd.read_csv("data/outputs/toxicity_bert_campus.csv")
    camp["text"] = camp["text"].fillna("").astype(str)
    camp["base_score"] = model.predict_proba(camp["text"])[:, 1]
    y = to_bool(camp["abusive"])
    b = camp["base_score"].values >= CUT
    t = camp["bert_score"].values >= CUT
    table(f"CAMPUS comments (cutoff {CUT} for both)", y, b, t)

    jig = pd.read_csv("data/outputs/toxicity_bert_jigsaw.csv")
    jig["text"] = jig["text"].fillna("").astype(str)
    jig["base_score"] = model.predict_proba(jig["text"])[:, 1]
    yj = to_bool(jig["abusive"])
    table("JIGSAW sample (same 2000 comments; toxic-bert may have seen some in training)",
          yj, jig["base_score"].values >= CUT, jig["bert_score"].values >= CUT)

    def show(title, mask, limit=15):
        print(f"\n{title}")
        for r in camp[mask].head(limit).itertuples():
            print(f"  [base {r.base_score:.2f} | bert {r.bert_score:.2f}] {r.text[:90]}")

    show("Abusive, caught by toxic-bert but missed by baseline:", y & t & ~b)
    show("Abusive, caught by baseline but missed by toxic-bert:", y & b & ~t)
    show("Abusive, missed by BOTH:", y & ~b & ~t)
    show("Normal comments the baseline wrongly flagged:", ~y & b)

    camp.to_csv("data/outputs/toxicity_compare_campus.csv", index=False)

if __name__ == "__main__":
    main()