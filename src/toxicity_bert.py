"""Module 7 check: how well does unitary/toxic-bert find abusive comments?
Runs on all 800 campus comments and a sample of the Jigsaw benchmark.
Saves the scores so they can be compared with the baseline without re-running."""
import pandas as pd
import torch
from transformers import pipeline

MODEL = "unitary/toxic-bert"
JIGSAW_N = 2000  # how many Jigsaw comments to test (more = slower)

def to_bool(s):
    return s.astype(str).str.strip().str.lower().isin(["true", "1", "1.0", "yes"]).values

def score(texts, clf):
    """Highest of the model's six scores (toxic, insult, threat, ...) per comment."""
    rows = clf(list(texts), batch_size=32, truncation=True, max_length=128,
               function_to_apply="sigmoid")
    return [max(d["score"] for d in row) for row in rows]

def report(name, y, s):
    print(f"\n{name}: {int(y.sum())} abusive out of {len(y)} comments")
    for cutoff in (0.3, 0.5, 0.7):
        flag = s >= cutoff
        tp = int((flag & y).sum())
        fp = int((flag & ~y).sum())
        fn = int((~flag & y).sum())
        prec = tp / (tp + fp) if tp + fp else 0
        rec = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
        print(f"  cutoff {cutoff}: caught {tp} of {tp + fn} abusive, "
              f"{fp} false alarms | of flagged, {prec:.0%} truly abusive | "
              f"of abusive, {rec:.0%} caught | F1 {f1:.2f}")

def main():
    device = 0 if torch.cuda.is_available() else -1
    clf = pipeline("text-classification", model=MODEL, top_k=None, device=device)

    # 1) Campus comments (all 800: toxic-bert never trained on them, so this is fair)
    camp = pd.read_csv("data/processed/campus_feedback.csv")
    camp["text"] = camp["text"].fillna("")
    camp["bert_score"] = score(camp["text"], clf)
    y = to_bool(camp["abusive"])
    report("CAMPUS comments", y, camp["bert_score"].values)
    camp[["id", "facility", "text", "abusive", "bert_score"]].to_csv(
        "data/outputs/toxicity_bert_campus.csv", index=False)

    print("\nAbusive campus comments that toxic-bert MISSED (cutoff 0.5):")
    for r in camp[y & (camp["bert_score"].values < 0.5)].itertuples():
        print(f"  [{r.bert_score:.2f}] {r.text[:100]}")
    print("\nNormal campus comments toxic-bert wrongly FLAGGED (cutoff 0.5):")
    for r in camp[~y & (camp["bert_score"].values >= 0.5)].itertuples():
        print(f"  [{r.bert_score:.2f}] {r.text[:100]}")

    # 2) Jigsaw benchmark (outside data, English)
    jig = pd.read_csv("data/processed/jigsaw_abusive_sample.csv")
    jig = jig.sample(n=min(JIGSAW_N, len(jig)), random_state=42).reset_index(drop=True)
    jig["text"] = jig["text"].fillna("")
    jig["bert_score"] = score(jig["text"], clf)
    report("JIGSAW sample", to_bool(jig["abusive"]), jig["bert_score"].values)
    jig[["id", "text", "abusive", "bert_score"]].to_csv(
        "data/outputs/toxicity_bert_jigsaw.csv", index=False)

if __name__ == "__main__":
    main()