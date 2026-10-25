"""Step 7. python -m src.evaluate validation
          python -m src.evaluate test --final        (RUN ONCE, at the very end)
          python -m src.evaluate edurabsa --final    (EduRABSA test benchmark, also once)
          python -m src.evaluate gold --final        (needs data/processed/gold_test.csv)"""
import json, sys
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix
from src.aspects_hybrid import extract_aspects
from src.preprocess import clause_with_term
from src.sentiment import predict_sentiment

LABELS = ["positive", "neutral", "negative"]
split = sys.argv[1] if len(sys.argv) > 1 else "validation"
if split != "validation" and "--final" not in sys.argv:
    sys.exit("Refusing: test-type sets need --final (run once, at the very end).")

def sent_report(name, gold, pred):
    print(f"{name}: accuracy={accuracy_score(gold, pred):.3f}  macro-F1={f1_score(gold, pred, average='macro', labels=LABELS, zero_division=0):.3f}  n={len(gold)}")
    print(confusion_matrix(gold, pred, labels=LABELS), "rows=gold cols=pred", LABELS)

def aspect_report(df):
    tp = fp = fn = 0
    for _, r in df.iterrows():
        gold = {a["category"] for a in json.loads(r["aspects"])}
        pred = {a["category"] for a in extract_aspects(r["text"], r["facility"])} - {"general"}
        tp += len(gold & pred); fp += len(pred - gold); fn += len(gold - pred)
    p, rc = tp / (tp + fp), tp / (tp + fn)
    print(f"ASPECT: precision={p:.3f} recall={rc:.3f} F1={2*p*rc/(p+rc):.3f}")

if split == "edurabsa":
    d = pd.read_csv("data/processed/unified_edurabsa_test.csv")
    d = d[d["sentiment"].isin(LABELS)]
    pred = [predict_sentiment(clause_with_term(t, a), a) for t, a in zip(d["text"], d["aspect_term"])]
    sent_report("EduRABSA test (domain transfer)", d["sentiment"], pred)
    cf = d["category"] == "University - Campus & facilities"
    sent_report("  campus & facilities subset", d[cf]["sentiment"], [p for p, m in zip(pred, cf) if m])
elif split == "gold":
    d = pd.read_csv("data/processed/gold_test.csv")
    d = d[d["verified"].astype(str).str.upper() == "OK"]
    rows = [(a["sentiment"], predict_sentiment(clause_with_term(t, a["aspect_term"]), a["aspect_term"]))
            for t, asp in zip(d["text"], d["aspects"]) for a in json.loads(asp)]
    sent_report("GOLD (hand-verified)", [r[0] for r in rows], [r[1] for r in rows])
else:
    c = pd.read_csv(f"data/processed/{split}_comments.csv")
    aspect_report(c)
    a = pd.read_csv(f"data/processed/{split}_aspects.csv")
    pred = [predict_sentiment(clause_with_term(t, x), x) for t, x in zip(a["text"], a["aspect_term"])]
    sent_report(f"SENTIMENT ({split}, gold aspect terms)", a["sentiment"], pred)
