"""python -m src.quick_check_sentiment train|validation
Scores the clause containing each gold aspect term; prints macro-F1, confusion matrix, errors."""
import sys
import pandas as pd
from sklearn.metrics import f1_score, confusion_matrix, classification_report
from src.preprocess import clause_with_term
from src.sentiment import score_clause, label_from_score

LABELS = ["positive", "neutral", "negative"]

def load(split):
    df = pd.read_csv(f"data/processed/{split}_aspects.csv")
    df["clause"] = [clause_with_term(t, a) for t, a in zip(df["text"], df["aspect_term"])]
    df["score"] = df["clause"].map(score_clause)
    return df

def evaluate(df, pos_t=None, neg_t=None, no_evidence=None):
    pred = df["score"].map(lambda s: label_from_score(s, pos_t, neg_t, no_evidence))
    return pred, f1_score(df["sentiment"], pred, average="macro", labels=LABELS, zero_division=0)

if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "train"
    df = load(split)
    pred, f1 = evaluate(df)
    print(f"{split}: macro-F1={f1:.3f}  accuracy={(pred == df['sentiment']).mean():.3f}  n={len(df)}")
    print(confusion_matrix(df["sentiment"], pred, labels=LABELS), " rows=gold cols=pred", LABELS)
    print(classification_report(df["sentiment"], pred, labels=LABELS, zero_division=0))
    err = df[pred != df["sentiment"]]
    for _, r in err.head(25).iterrows():
        print(f"gold={r.sentiment:8s} score={r.score:+.2f} | {r.clause}")
