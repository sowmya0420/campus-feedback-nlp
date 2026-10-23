"""The single entry point. analyse() is used by batch mode, the Streamlit form and evaluation.
Batch: python -m src.pipeline data/processed/validation_comments.csv   (default: all 3 splits)"""
import sys, joblib, pandas as pd
from src.aspects import extract_aspects
from src.sentiment import predict_sentiment

_tox = None
def is_abusive(text, thr=0.5):
    """Swappable: replace with DistilBERT / toxic-bert later, same signature."""
    global _tox
    if _tox is None:
        _tox = joblib.load("models/toxicity_tfidf_logreg.joblib")
    return bool(_tox.predict_proba([str(text)])[0, 1] >= thr)

def analyse(text, facility):
    """-> {'abusive': bool, 'aspects': [{'category','aspect_term','clause','sentiment'}]}"""
    aspects = []
    for a in extract_aspects(text, facility):
        aspects.append({**a, "sentiment": predict_sentiment(a["clause"], a["aspect_term"] or a["category"])})
    return {"abusive": is_abusive(text), "aspects": aspects}

def run_batch(paths, out="data/outputs/predictions.csv"):
    df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    rows = []
    for _, r in df.iterrows():
        res = analyse(r["text"], r["facility"])
        for a in res["aspects"]:
            rows.append({"id": r["id"], "facility": r["facility"], "text": r["text"],
                         "category": a["category"], "sentiment": a["sentiment"], "abusive": res["abusive"]})
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out}: {len(rows)} aspect rows from {len(df)} comments")

if __name__ == "__main__":
    paths = sys.argv[1:] or [f"data/processed/{s}_comments.csv" for s in ("train", "validation", "test")]
    run_batch(paths)
