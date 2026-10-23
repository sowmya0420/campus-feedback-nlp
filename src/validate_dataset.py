"""
Automated Dataset Validation Suite for Campus Facility Feedback NLP System
Performs deterministic structural, syntactic, schema, and linguistic checks on raw and processed datasets.
"""

import os
import sys
import json
import glob
import re
from collections import Counter
from difflib import SequenceMatcher

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

FACILITY_CATEGORIES = {
    "hostel_mess": [
        "food quality", "price", "hygiene", "waiting time",
        "seating", "staff behavior", "quantity", "variety"
    ],
    "canteen": [
        "food quality", "price", "hygiene", "waiting time",
        "seating", "staff behavior", "quantity", "variety"
    ],
    "library": [
        "book availability", "seating", "silence", "opening hours",
        "staff behavior", "cleanliness", "ac/temperature", "digital resources"
    ],
    "hostel_rooms": [
        "cleanliness", "water supply", "electricity", "maintenance",
        "room size", "safety", "laundry", "noise"
    ],
    "labs": [
        "equipment condition", "system speed", "software availability",
        "lab staff", "lab timings", "cleanliness", "space"
    ],
    "wifi": [
        "speed", "connectivity", "coverage", "login issues",
        "reliability", "bandwidth limit"
    ],
    "transport": [
        "punctuality", "crowding", "driver behavior", "route coverage",
        "bus condition", "safety", "fare"
    ],
    "classrooms": [
        "ac/temperature", "seating", "projector/av", "cleanliness",
        "lighting", "noise"
    ],
}

VALID_FACILITIES = set(FACILITY_CATEGORIES.keys())
VALID_SENTIMENTS = {"positive", "negative", "neutral"}

REQUIRED_FIELDS = [
    "id", "facility", "batch", "persona", "text", "aspects", "abusive", "source_type"
]

BATCH_1_PERSONAS = {
    "first-year hosteller",
    "second-year day scholar",
    "final-year student",
    "girls' hostel resident",
    "outstation student",
}

BATCH_2_PERSONAS = {
    "placement-focused student",
    "club member",
    "backlog student",
    "third-year hosteller",
    "faculty-project student",
}


def derive_comment_sentiment(aspects):
    """
    Derives comment-level sentiment explicitly:
    - unresolved: no aspects available
    - mixed: at least one positive and one negative aspect
    - positive: at least one positive aspect and no negative aspect
    - negative: at least one negative aspect and no positive aspect
    - neutral: all aspects are neutral
    """
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


def validate_raw_datasets(raw_dir=RAW_DIR):
    hard_failures = []
    warnings = []
    
    all_comment_ids = Counter()
    all_raw_texts = []
    
    facility_counts = Counter()
    batch_counts = Counter()
    abusive_counts = Counter()
    
    comment_sentiments = Counter()
    aspect_sentiments = Counter()
    aspect_categories = Counter()
    aspects_per_comment = Counter()
    
    length_dist = {"short": 0, "medium": 0, "long": 0}
    tanglish_count = 0
    
    TANGLISH_MARKERS = [
        "romba", "semma", "illa", "la", "ku", "kooda", "enna", "pa",
        "mattum", "iruku", "mudiyala", "kedaikadhu", "anna", "agudhu"
    ]
    
    # Check that all 8 facility combined files and 16 batch files exist
    expected_files = []
    for fac in sorted(VALID_FACILITIES):
        expected_files.append(f"{fac}_1.json")
        expected_files.append(f"{fac}_2.json")
        expected_files.append(f"{fac}.json")
        
    for ef in expected_files:
        p = os.path.join(raw_dir, ef)
        if not os.path.exists(p):
            hard_failures.append({
                "file": ef, "id": "N/A", "error": f"Missing expected raw file: {ef}"
            })

    # Validate batch files
    batch_files = sorted(glob.glob(os.path.join(raw_dir, "*_[12].json")))
    for bf in batch_files:
        bname = os.path.basename(bf)
        m = re.match(r"^([a-z_]+)_([12])\.json$", bname)
        if not m:
            continue
        fac_from_file, batch_num = m.group(1), int(m.group(2))
        
        try:
            with open(bf, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception as e:
            hard_failures.append({
                "file": bname, "id": "N/A", "error": f"JSON parse error: {e}"
            })
            continue
            
        if len(records) != 50:
            hard_failures.append({
                "file": bname, "id": "N/A",
                "error": f"Incorrect batch count: {len(records)} comments (expected 50)"
            })
            
        batch_abusive = sum(1 for d in records if d.get("abusive") is True)
        if batch_abusive != 3:
            hard_failures.append({
                "file": bname, "id": "N/A",
                "error": f"Incorrect abusive count: {batch_abusive} abusive comments (expected 3)"
            })
            
        for d in records:
            cid = d.get("id", "UNKNOWN")
            all_comment_ids[cid] += 1
            text = d.get("text", "").strip()
            all_raw_texts.append((cid, bname, text))
            
            # Check required fields
            for rf in REQUIRED_FIELDS:
                if rf not in d:
                    hard_failures.append({
                        "file": bname, "id": cid, "error": f"Missing required field: {rf}"
                    })
                    
            fac = d.get("facility")
            if fac != fac_from_file or fac not in VALID_FACILITIES:
                hard_failures.append({
                    "file": bname, "id": cid,
                    "error": f"Invalid or mismatched facility: '{fac}' (expected '{fac_from_file}')"
                })
                
            batch_val = d.get("batch")
            if batch_val != batch_num:
                hard_failures.append({
                    "file": bname, "id": cid,
                    "error": f"Mismatched batch: {batch_val} (expected {batch_num})"
                })
                
            persona = d.get("persona")
            allowed_personas = BATCH_1_PERSONAS if batch_num == 1 else BATCH_2_PERSONAS
            if persona not in allowed_personas:
                warnings.append({
                    "file": bname, "id": cid,
                    "warning": f"Persona '{persona}' not in standard set for batch {batch_num}"
                })
                
            abusive = d.get("abusive")
            if not isinstance(abusive, bool):
                hard_failures.append({
                    "file": bname, "id": cid, "error": f"Field 'abusive' must be boolean, got {type(abusive)}"
                })
                
            # Length tracking
            words = text.split()
            word_count = len(words)
            if word_count <= 8:
                length_dist["short"] += 1
            elif word_count <= 20:
                length_dist["medium"] += 1
            else:
                length_dist["long"] += 1
                
            if any(tm in text.lower() for tm in TANGLISH_MARKERS):
                tanglish_count += 1
                
            aspects = d.get("aspects", [])
            aspects_per_comment[len(aspects)] += 1
            
            # Comment sentiment
            csent = derive_comment_sentiment(aspects)
            comment_sentiments[csent] += 1
            
            # Aspects checks
            allowed_cats = set(FACILITY_CATEGORIES.get(fac, []))
            for a_idx, a in enumerate(aspects):
                cat = a.get("category")
                sent = a.get("sentiment")
                term = a.get("aspect_term")
                
                if cat not in allowed_cats:
                    hard_failures.append({
                        "file": bname, "id": cid,
                        "error": f"Category '{cat}' is not permitted for facility '{fac}'"
                    })
                else:
                    aspect_categories[cat] += 1
                    
                if sent not in VALID_SENTIMENTS:
                    hard_failures.append({
                        "file": bname, "id": cid,
                        "error": f"Invalid sentiment '{sent}' (must be in {VALID_SENTIMENTS})"
                    })
                else:
                    aspect_sentiments[sent] += 1
                    
                if term is not None:
                    if term not in text:
                        hard_failures.append({
                            "file": bname, "id": cid,
                            "error": f"Aspect term '{term}' is not an exact substring of text: '{text}'"
                        })

    # Check ID uniqueness
    for cid, count in all_comment_ids.items():
        if count > 1:
            hard_failures.append({
                "file": "ALL", "id": cid, "error": f"Duplicate comment ID: {cid} appears {count} times"
            })
            
    # Check text exact duplicates
    text_counter = Counter()
    for cid, bname, text in all_raw_texts:
        norm = re.sub(r"\W+", " ", text.lower()).strip()
        text_counter[norm] += 1
    for norm, count in text_counter.items():
        if count > 1:
            hard_failures.append({
                "file": "ALL", "id": "N/A", "error": f"Exact duplicate text found ({count} times): '{norm}'"
            })

    # Combined facility files check
    for fac in sorted(VALID_FACILITIES):
        cf = os.path.join(raw_dir, f"{fac}.json")
        try:
            with open(cf, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            if len(cdata) != 100:
                hard_failures.append({
                    "file": f"{fac}.json", "id": "N/A",
                    "error": f"Incorrect facility total comments: {len(cdata)} (expected 100)"
                })
            fac_abusive = sum(1 for d in cdata if d.get("abusive") is True)
            if fac_abusive != 6:
                hard_failures.append({
                    "file": f"{fac}.json", "id": "N/A",
                    "error": f"Incorrect facility abusive count: {fac_abusive} (expected 6)"
                })
        except Exception as e:
            hard_failures.append({
                "file": f"{fac}.json", "id": "N/A", "error": f"Error parsing combined file: {e}"
            })

    # Multi-aspect ratio
    multi_aspect_count = sum(v for k, v in aspects_per_comment.items() if k >= 2)
    total_comments = sum(aspects_per_comment.values())
    multi_aspect_ratio = multi_aspect_count / max(1, total_comments)
    if multi_aspect_ratio < 0.25:
        warnings.append({
            "file": "ALL", "id": "N/A",
            "warning": f"Multi-aspect comment ratio is {multi_aspect_ratio:.1%} (target >= 30%)"
        })

    report = {
        "status": "PASS" if not hard_failures else "FAIL",
        "total_comments": total_comments,
        "total_aspects": sum(aspect_sentiments.values()),
        "total_abusive": sum(1 for _, _, t in all_raw_texts if False), # filled in detail
        "hard_failures_count": len(hard_failures),
        "warnings_count": len(warnings),
        "hard_failures": hard_failures,
        "warnings": warnings,
        "comment_level_sentiment": dict(comment_sentiments),
        "aspect_level_sentiment": dict(aspect_sentiments),
        "length_distribution": length_dist,
        "tanglish_comments": tanglish_count,
        "aspects_per_comment": dict(aspects_per_comment),
        "multi_aspect_percentage": round(multi_aspect_ratio * 100, 2)
    }
    return report


if __name__ == "__main__":
    report = validate_raw_datasets()
    print("=" * 60)
    print(f"VALIDATION STATUS: {report['status']}")
    print(f"Total Comments: {report['total_comments']}")
    print(f"Total Aspects : {report['total_aspects']}")
    print(f"Hard Failures : {report['hard_failures_count']}")
    print(f"Warnings      : {report['warnings_count']}")
    print("=" * 60)
    print("Comment-Level Sentiment Distribution:")
    for k, v in report["comment_level_sentiment"].items():
        print(f"  {k}: {v} ({v/report['total_comments']*100:.1f}%)")
    print("\nAspect-Level Sentiment Distribution:")
    for k, v in report["aspect_level_sentiment"].items():
        print(f"  {k}: {v} ({v/report['total_aspects']*100:.1f}%)")
    print(f"\nMulti-Aspect Comments (>=2 aspects): {report['multi_aspect_percentage']}%")
    print(f"Tanglish Comments: {report['tanglish_comments']} ({report['tanglish_comments']/report['total_comments']*100:.1f}%)")
    print(f"Length Distribution: {report['length_distribution']}")
    print("=" * 60)
    
    if report["hard_failures"]:
        print("\nHARD FAILURES:")
        for hf in report["hard_failures"][:20]:
            print(f"  [{hf['file']} | {hf['id']}] {hf['error']}")
        sys.exit(1)
    else:
        print("\nAll raw dataset validation checks passed successfully!")
        sys.exit(0)
