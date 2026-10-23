"""
Dataset Adapters for Campus Facility Feedback NLP System

Converts external datasets (EduRABSA, Jigsaw) and the synthetic campus feedback
into separate, well-documented, standardized schemas without cross-contaminating facility data.

Datasets:
- EduRABSA (Hua et al., 2025): Course/Staff Aspect-Based Sentiment Analysis.
- Jigsaw Toxic Comment Classification: Abusive content benchmark dataset.
- Synthetic Campus Feedback: Campus facility aspect-based sentiment and abuse dataset.
"""

import os
import json
import pandas as pd
import numpy as np

PROCESSED_DIR = "data/processed"
EXTERNAL_DIR = "data/external"
SEED = 42

UNIFIED_COLS = [
    "id", "source", "domain", "text", "aspect_term", "category", "opinion", "sentiment"
]


def from_edurabsa(path):
    """
    Adapter for EduRABSA jsonl files (Hua et al., 2025).
    Extracts educational course/staff/university ABSA annotations.
    """
    if not os.path.exists(path):
        print(f"[!] EduRABSA file not found at: {path}")
        return pd.DataFrame(columns=UNIFIED_COLS)
        
    df = pd.read_json(path, lines=True)
    rows = []
    for r in df.itertuples():
        for a in r.output:
            term = None if a.get("aspect") in (None, "null", "") else a["aspect"]
            cat = a.get("category", "")
            domain = cat.split(" - ")[0].lower() if cat else "education"
            rows.append({
                "id": r.id,
                "source": "edurabsa",
                "domain": domain,
                "text": r.text,
                "aspect_term": term,
                "category": cat,
                "opinion": a.get("opinion"),
                "sentiment": str(a.get("sentiment", "")).lower(),
            })
    return pd.DataFrame(rows, columns=UNIFIED_COLS)


def from_synthetic(path):
    """
    Adapter for synthetic campus aspect data.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Synthetic aspects file not found: {path}")
        
    df = pd.read_csv(path)
    out = pd.DataFrame({
        "id": df["id"],
        "source": "synthetic",
        "domain": df["facility"],
        "text": df["text"],
        "aspect_term": df["aspect_term"],
        "category": df["category"],
        "opinion": None,
        "sentiment": df["sentiment"].astype(str).str.lower(),
    })
    return out[UNIFIED_COLS]


def from_jigsaw(path, sample_n=5000, seed=SEED):
    """
    Adapter for Jigsaw Toxic Comment Classification dataset.
    Extracts a balanced evaluation sample for abusive content detection.
    Keeps labels strictly separate from campus facility feedback.
    """
    if not os.path.exists(path):
        print(f"[!] Jigsaw file not found at: {path}")
        return None
        
    df = pd.read_csv(path)
    # Define abusive if any toxic, severe_toxic, obscene, threat, insult, or identity_hate is 1
    toxic_cols = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    df["abusive"] = (df[toxic_cols].sum(axis=1) > 0)
    
    # Stratified sample of size sample_n (balanced 50% toxic, 50% non-toxic)
    pos = df[df["abusive"] == True]
    neg = df[df["abusive"] == False]
    
    half = sample_n // 2
    pos_sample = pos.sample(n=min(half, len(pos)), random_state=seed)
    neg_sample = neg.sample(n=min(half, len(neg)), random_state=seed)
    
    sample_df = pd.concat([pos_sample, neg_sample]).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    
    out = pd.DataFrame({
        "id": sample_df["id"],
        "source": "jigsaw",
        "text": sample_df["comment_text"],
        "abusive": sample_df["abusive"],
        "toxic": sample_df["toxic"],
        "severe_toxic": sample_df["severe_toxic"],
        "obscene": sample_df["obscene"],
        "threat": sample_df["threat"],
        "insult": sample_df["insult"],
        "identity_hate": sample_df["identity_hate"]
    })
    return out


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # 1. EduRABSA processing
    for split in ["train", "test"]:
        in_p = os.path.join(EXTERNAL_DIR, "edurabsa", f"{split}.jsonl")
        out_p = os.path.join(PROCESSED_DIR, f"unified_edurabsa_{split}.csv")
        d = from_edurabsa(in_p)
        if len(d):
            d.to_csv(out_p, index=False)
            print(f"[Adapter] EduRABSA {split}: {len(d)} aspect rows across {d['id'].nunique()} reviews -> {out_p}")

    # 2. Synthetic campus feedback
    synth_p = os.path.join(PROCESSED_DIR, "campus_aspects.csv")
    s = from_synthetic(synth_p)
    synth_out = os.path.join(PROCESSED_DIR, "unified_synthetic.csv")
    s.to_csv(synth_out, index=False)
    print(f"[Adapter] Synthetic: {len(s)} aspect rows across {s['id'].nunique()} comments -> {synth_out}")
    
    # 3. Jigsaw Toxic Benchmark processing
    jigsaw_in = os.path.join(EXTERNAL_DIR, "jigsaw", "train.csv")
    j = from_jigsaw(jigsaw_in, sample_n=5000, seed=SEED)
    if j is not None:
        j_out = os.path.join(PROCESSED_DIR, "jigsaw_abusive_sample.csv")
        j.to_csv(j_out, index=False)
        print(f"[Adapter] Jigsaw benchmark sample: {len(j)} comments (Abusive: {j['abusive'].sum()}) -> {j_out}")


if __name__ == "__main__":
    main()
