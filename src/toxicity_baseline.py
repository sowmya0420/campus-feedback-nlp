"""Module 7 baseline: TF-IDF + LogisticRegression trained on Jigsaw train (binary toxic).
The 5,000-row evaluation sample is EXCLUDED from training (same source file, so it would leak).
Evaluated on (a) that sample and (b) all 800 synthetic campus comments (48 abusive).
Run: python -m src.toxicity_baseline"""
import joblib, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
from src import config

full = pd.read_csv("data/external/jigsaw/train.csv")
sample = pd.read_csv("data/processed/jigsaw_abusive_sample.csv")
train = full[~full["id"].isin(set(sample["id"]))]
print(f"train rows={len(train)} (removed {len(full)-len(train)} sample rows)")

model = make_pipeline(
    TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=3, max_features=200_000, sublinear_tf=True),
    LogisticRegression(max_iter=1000, class_weight="balanced", C=4.0),
)
model.fit(train["comment_text"].astype(str), train["toxic"])
joblib.dump(model, "models/toxicity_tfidf_logreg.joblib")

def report(name, texts, y, thr=0.5):
    p = (model.predict_proba(texts.astype(str))[:, 1] >= thr).astype(int)
    pr, rc, f1, _ = precision_recall_fscore_support(y.astype(int), p, average="binary", zero_division=0)
    print(f"{name:34s} P={pr:.3f} R={rc:.3f} F1={f1:.3f}  (n={len(y)}, positives={int(y.sum())})")
    print(confusion_matrix(y.astype(int), p))

report("Jigsaw 5k sample", sample["text"], sample["abusive"])
syn = pd.concat([pd.read_csv(f"data/processed/{s}_comments.csv") for s in ["train", "validation", "test"]])
report("Synthetic campus (800, 48 abusive)", syn["text"], syn["abusive"])
missed = syn[(syn["abusive"]) & (model.predict_proba(syn["text"].astype(str))[:, 1] < 0.5)]
print("\nabusive synthetic comments MISSED (Tanglish/slang gap):")
for t in missed["text"].head(10): print("  -", t)
