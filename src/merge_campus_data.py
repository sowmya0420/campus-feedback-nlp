"""
Merge and format campus facility feedback JSON files into processed CSV datasets.

Input : data/raw/<facility>.json (100 comments each across 8 facilities)
Output: data/processed/campus_feedback.csv (800 comments)
        data/processed/campus_aspects.csv  (one row per aspect annotation)
"""

import os
import json
import glob
import re
import pandas as pd
from collections import Counter

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"

FACILITIES = [
    "hostel_mess", "canteen", "library", "hostel_rooms",
    "labs", "wifi", "transport", "classrooms"
]


def derive_comment_sentiment(aspects):
    if not aspects:
        return "unresolved"
    sents = {a.get("sentiment") for a in aspects if a.get("sentiment")}
    if not sents:
        return "unresolved"
    if "positive" in sents and "negative" in sents:
        return "mixed"
    elif "positive" in sents and "negative" not in sents:
        return "positive"
    elif "negative" in sents and "positive" not in sents:
        return "negative"
    elif sents == {"neutral"}:
        return "neutral"
    return "unresolved"


def merge_data(raw_dir=RAW_DIR, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    
    comments = []
    aspect_rows = []
    
    for fac in sorted(FACILITIES):
        combined_path = os.path.join(raw_dir, f"{fac}.json")
        if not os.path.exists(combined_path):
            raise FileNotFoundError(f"Missing combined facility file: {combined_path}")
            
        with open(combined_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for item in data:
            cid = item["id"]
            leg_id = item.get("legacy_id")
            batch = item["batch"]
            persona = item["persona"]
            persona_status = item.get("persona_status", "assigned_for_balance")
            text = item["text"].strip()
            abusive = bool(item.get("abusive", False))
            source_type = item.get("source_type", "synthetic")
            provenance = item.get("provenance", "unknown")
            aspects = item.get("aspects", [])
            
            csent = derive_comment_sentiment(aspects)
            
            comment_record = {
                "id": cid,
                "legacy_id": leg_id if leg_id else "",
                "facility": fac,
                "batch": batch,
                "persona": persona,
                "persona_status": persona_status,
                "text": text,
                "aspects": json.dumps(aspects, ensure_ascii=False),
                "abusive": abusive,
                "source_type": source_type,
                "provenance": provenance,
                "comment_sentiment": csent,
                "aspect_count": len(aspects)
            }
            comments.append(comment_record)
            
            for a in aspects:
                aspect_rows.append({
                    "id": cid,
                    "legacy_id": leg_id if leg_id else "",
                    "facility": fac,
                    "batch": batch,
                    "persona": persona,
                    "text": text,
                    "aspect_term": a.get("aspect_term") if a.get("aspect_term") is not None else "",
                    "category": a.get("category"),
                    "sentiment": a.get("sentiment"),
                    "abusive": abusive,
                    "source_type": source_type,
                    "provenance": provenance
                })

    df_comments = pd.DataFrame(comments)
    df_aspects = pd.DataFrame(aspect_rows)
    
    # Save processed CSVs
    feedback_csv = os.path.join(out_dir, "campus_feedback.csv")
    aspects_csv = os.path.join(out_dir, "campus_aspects.csv")
    
    df_comments.to_csv(feedback_csv, index=False)
    df_aspects.to_csv(aspects_csv, index=False)
    
    print(f"[Merge] Wrote {len(df_comments)} comments to {feedback_csv}")
    print(f"[Merge] Wrote {len(df_aspects)} aspects to {aspects_csv}")
    print(f"[Merge] Facilities ({df_comments['facility'].nunique()}):")
    print(df_comments["facility"].value_counts().to_string())
    print(f"\n[Merge] Abusive comments: {df_comments['abusive'].sum()} / {len(df_comments)}")
    print(f"[Merge] Comment-level sentiments:\n{df_comments['comment_sentiment'].value_counts().to_string()}")
    print(f"[Merge] Aspect-level sentiments:\n{df_aspects['sentiment'].value_counts().to_string()}")
    
    return df_comments, df_aspects


if __name__ == "__main__":
    merge_data()
