import os
import sys
import pandas as pd
from flask import Flask, render_template, request, jsonify

# Set base directory to the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

app = Flask(__name__)
DATA_OUT = os.path.join(BASE_DIR, "data", "outputs")

# Canonical mapping of the 8 campus facilities used across all pages
FACILITY_DISPLAY_NAMES = {
    "canteen": "Canteen",
    "classrooms": "Classrooms",
    "hostel_mess": "Hostel Mess",
    "hostel_rooms": "Hostel Rooms",
    "labs": "Labs",
    "library": "Library",
    "transport": "Transport",
    "wifi": "Wi-Fi"
}

def get_facility_display_name(fac):
    if not fac:
        return ""
    key = str(fac).lower().strip()
    return FACILITY_DISPLAY_NAMES.get(key, key.replace("_", " ").title())

# -----------------------------------------------------------------------------
# Machine Learning Model Pipeline Preloading
# Preloads DistilBERT aspect, DistilBERT sentiment, and Toxic-BERT once on startup
# -----------------------------------------------------------------------------
PIPELINE_READY = False
PIPELINE_ERROR = None
pipeline_analyse = None
pipeline_mod = None

print("Loading models (DistilBERT aspect, DistilBERT sentiment, Toxic-BERT)...", flush=True)
try:
    from src.pipeline import analyse as _analyse
    import src.pipeline as _mod
    pipeline_analyse = _analyse
    pipeline_mod = _mod
    # Warm up with a simple sentence to load model weights into memory once
    _ = pipeline_analyse("campus feedback system test", "library")
    PIPELINE_READY = True
    print("Models loaded successfully and ready for inference.", flush=True)
except Exception as e:
    PIPELINE_ERROR = str(e)
    print(f"Warning: Models failed to load on startup: {e}", flush=True)

# Cached data loaders
def load_ratings():
    path = os.path.join(DATA_OUT, "ratings.csv")
    df = pd.read_csv(path)
    df["display_facility"] = df["facility"].apply(get_facility_display_name)
    return df

def load_issues():
    path = os.path.join(DATA_OUT, "issues.csv")
    df = pd.read_csv(path)
    df["display_facility"] = df["facility"].apply(get_facility_display_name)
    return df

def load_summaries():
    path = os.path.join(DATA_OUT, "summaries.csv")
    df = pd.read_csv(path)
    df["display_facility"] = df["facility"].apply(get_facility_display_name)
    return df

def load_predictions():
    path = os.path.join(DATA_OUT, "predictions.csv")
    df = pd.read_csv(path)
    df["display_facility"] = df["facility"].apply(get_facility_display_name)
    return df

# Global context for navigation and stats
@app.context_processor
def inject_global_data():
    return {
        "project_name": "Campus Facility Feedback Analysis System",
        "team_label": "Final Year NLP Project"
    }

# 1. HOME ROUTE
@app.route("/")
def home():
    ratings_df = load_ratings()
    issues_df = load_issues()
    pred_df = load_predictions()

    # Extract overall ratings per facility
    ov = ratings_df[ratings_df["category"] == "OVERALL"].copy()
    ov["rating"] = ov["rating"].round(2)
    ov = ov.sort_values("rating", ascending=False)

    # Key executive numbers
    total_comments = int(pred_df["id"].nunique())
    facility_count = int(ov["facility"].nunique())
    avg_rating = round(float(ov["rating"].mean()), 2)
    issues_count = int(len(issues_df))
    flagged_count = int(pred_df[pred_df["abusive"] == True]["id"].nunique())

    # Build facility cards data for quick view
    facilities_list = []
    for _, row in ov.iterrows():
        fac_key = row["facility"]
        fac_issues = issues_df[issues_df["facility"] == fac_key]
        top_issue = fac_issues.iloc[0]["category"] if not fac_issues.empty else "No major issue"
        issue_cnt = len(fac_issues)
        comment_count = int(pred_df[pred_df["facility"] == fac_key]["id"].nunique())

        facilities_list.append({
            "id": fac_key,
            "name": row["display_facility"],
            "rating": float(row["rating"]),
            "top_issue": top_issue.title(),
            "issues_count": issue_cnt,
            "comments_count": comment_count,
            "status": "Good" if row["rating"] >= 2.6 else ("Moderate" if row["rating"] >= 2.45 else "Needs Improvement")
        })

    stats = {
        "total_comments": total_comments,
        "facility_count": facility_count,
        "avg_rating": avg_rating,
        "issues_count": issues_count,
        "flagged_count": flagged_count
    }

    return render_template("home.html", stats=stats, facilities=facilities_list, active_page="home")

# 2. RATINGS ROUTE
@app.route("/ratings")
def ratings():
    df = load_ratings()
    
    # Overall facility ratings sorted by score
    ov = df[df["category"] == "OVERALL"].sort_values("rating", ascending=False)
    facilities_list = [
        {"id": row["facility"], "name": row["display_facility"], "rating": round(float(row["rating"]), 2)}
        for _, row in ov.iterrows()
    ]
    
    # Unique topics/categories (excluding OVERALL)
    topics_list = sorted([c for c in df["category"].unique() if c != "OVERALL"])
    
    # Campus average
    campus_avg = round(float(ov["rating"].mean()), 2)
    
    # Prepare clean records for sortable table and interactive chart
    clean_df = df.copy()
    clean_df["rating"] = clean_df["rating"].round(2)
    clean_df["mentions"] = clean_df["mentions"].astype(int)
    
    records = []
    for _, r in clean_df.iterrows():
        is_ov = (r["category"] == "OVERALL")
        pos = None if is_ov or pd.isna(r["positive"]) else int(r["positive"])
        neu = None if is_ov or pd.isna(r["neutral"]) else int(r["neutral"])
        neg = None if is_ov or pd.isna(r["negative"]) else int(r["negative"])
        neg_share = None if is_ov or pd.isna(r["negative_share"]) else round(float(r["negative_share"]) * 100, 1)
        
        records.append({
            "facility": r["facility"],
            "display_facility": r["display_facility"],
            "category": r["category"],
            "rating": float(r["rating"]),
            "mentions": int(r["mentions"]),
            "positive": pos,
            "neutral": neu,
            "negative": neg,
            "negative_share": neg_share,
            "is_overall": is_ov
        })
        
    return render_template(
        "ratings.html",
        active_page="ratings",
        facilities=facilities_list,
        topics=topics_list,
        campus_avg=campus_avg,
        ratings_data=records
    )

# 3. RECURRING ISSUES ROUTE
@app.route("/issues")
def issues():
    issues_df = load_issues()
    pred_df = load_predictions()
    
    # Filter non-abusive negative comments for each issue
    clean_pred = pred_df[(~pred_df["abusive"]) & (pred_df["sentiment"] == "negative")].copy()
    
    # Facilities list for dropdown - all 8 canonical campus facilities
    facilities_list = [
        {"id": fac, "name": FACILITY_DISPLAY_NAMES[fac]}
        for fac in sorted(FACILITY_DISPLAY_NAMES.keys(), key=lambda k: FACILITY_DISPLAY_NAMES[k])
    ]
    
    # Slider min and max strictly calculated from issues.csv
    min_neg_share = round(float(issues_df["negative_share"].min() * 100), 1)
    max_neg_share = round(float(issues_df["negative_share"].max() * 100), 1)
    
    # Build issues records with matching verified comments
    issues_records = []
    for _, row in issues_df.iterrows():
        fac = row["facility"]
        cat = row["category"]
        
        # Match real comments from predictions.csv
        matching_comments = clean_pred[
            (clean_pred["facility"] == fac) & (clean_pred["category"] == cat)
        ]["text"].tolist()
        
        neg_pct = round(float(row["negative_share"] * 100), 1)
        
        issues_records.append({
            "facility": fac,
            "display_facility": row["display_facility"],
            "category": cat.title(),
            "rating": round(float(row["rating"]), 2),
            "mentions": int(row["mentions"]),
            "positive": int(row["positive"]),
            "neutral": int(row["neutral"]),
            "negative": int(row["negative"]),
            "negative_share": neg_pct,
            "comments": matching_comments,
            "comments_count": len(matching_comments)
        })
        
    return render_template(
        "issues.html",
        active_page="issues",
        facilities=facilities_list,
        slider_min=min_neg_share,
        slider_max=max_neg_share,
        issues_data=issues_records
    )

# 4. SUMMARIES ROUTE
@app.route("/summaries")
def summaries():
    sum_df = load_summaries()
    ratings_df = load_ratings()
    issues_df = load_issues()
    pred_df = load_predictions()
    
    ov = ratings_df[ratings_df["category"] == "OVERALL"].copy()
    
    facility_summaries = []
    for _, row in sum_df.iterrows():
        fac_key = row["facility"]
        display_name = row["display_facility"]
        summary_text = str(row["summary"]).strip()
        
        # Overall rating from ratings.csv
        ov_row = ov[ov["facility"] == fac_key]
        rating_val = round(float(ov_row.iloc[0]["rating"]), 2) if not ov_row.empty else 0.0
        
        # Total comments from predictions.csv
        comments_cnt = int(pred_df[pred_df["facility"] == fac_key]["id"].nunique())
        
        # Recurring issues for this facility from issues.csv
        fac_issues = issues_df[issues_df["facility"] == fac_key]
        issues_list = []
        for _, ir in fac_issues.iterrows():
            issues_list.append({
                "category": ir["category"].title(),
                "negative_share": round(float(ir["negative_share"] * 100), 1),
                "mentions": int(ir["mentions"])
            })
        issues_list.sort(key=lambda x: x["negative_share"], reverse=True)
        
        facility_summaries.append({
            "id": fac_key,
            "name": display_name,
            "rating": rating_val,
            "comments_count": comments_cnt,
            "issues_count": len(issues_list),
            "issues": issues_list,
            "summary": summary_text
        })
        
    return render_template(
        "summaries.html",
        active_page="summaries",
        facilities=facility_summaries
    )

# 5. FLAGGED COMMENTS ROUTE
@app.route("/flagged")
def flagged():
    pred_df = load_predictions()
    
    # Read toxicity_bert_campus.csv for bert_score
    tox_path = os.path.join(DATA_OUT, "toxicity_bert_campus.csv")
    tox_df = pd.read_csv(tox_path) if os.path.exists(tox_path) else pd.DataFrame()
    
    # Deduplicate 49 flagged comments by id
    flagged_df = pred_df[pred_df["abusive"] == True][["id", "facility", "text", "display_facility"]].drop_duplicates(subset=["id"]).copy()
    
    # Merge bert_score if available
    if not tox_df.empty and "bert_score" in tox_df.columns:
        flagged_df = pd.merge(flagged_df, tox_df[["id", "bert_score"]], on="id", how="left")
    else:
        flagged_df["bert_score"] = 0.5
        
    total_comments = int(pred_df["id"].nunique())
    flagged_count = int(len(flagged_df))
    moderation_rate = round((flagged_count / total_comments) * 100, 1)
    
    # Facility breakdown for small bar summary
    fac_counts = flagged_df["facility"].value_counts().to_dict()
    all_facilities = list(FACILITY_DISPLAY_NAMES.keys())
    facility_breakdown = [
        {
            "id": fac,
            "name": FACILITY_DISPLAY_NAMES[fac],
            "count": int(fac_counts.get(fac, 0))
        }
        for fac in all_facilities
    ]
    facility_breakdown.sort(key=lambda x: (-x["count"], x["name"]))
    
    records = []
    for _, r in flagged_df.iterrows():
        b_score = round(float(r["bert_score"]), 3) if pd.notna(r.get("bert_score")) else 0.5
        records.append({
            "id": r["id"],
            "facility": r["facility"],
            "display_facility": r["display_facility"],
            "text": str(r["text"]).strip(),
            "bert_score": b_score,
            "bert_pct": round(b_score * 100, 1)
        })
        
    # Sort initially by toxicity score descending
    records.sort(key=lambda x: x["bert_score"], reverse=True)
    
    return render_template(
        "flagged.html",
        active_page="flagged",
        total_comments=total_comments,
        flagged_count=flagged_count,
        moderation_rate=moderation_rate,
        facility_breakdown=facility_breakdown,
        flagged_comments=records
    )

# 6. SUBMIT FEEDBACK ROUTE
@app.route("/submit")
def submit():
    facilities = [
        {"id": fac, "name": FACILITY_DISPLAY_NAMES[fac]}
        for fac in sorted(FACILITY_DISPLAY_NAMES.keys(), key=lambda k: FACILITY_DISPLAY_NAMES[k])
    ]
    return render_template(
        "submit.html",
        active_page="submit",
        facilities=facilities,
        models_ready=PIPELINE_READY,
        model_error=PIPELINE_ERROR
    )

@app.route("/api/analyse", methods=["POST"])
def api_analyse():
    if not PIPELINE_READY:
        return jsonify({
            "success": False,
            "error": "Machine learning models could not be loaded into memory: " + str(PIPELINE_ERROR or "Check model files in models/.")
        }), 503

    data = request.get_json(silent=True) or request.form
    text = (data.get("text") or "").strip()
    facility = (data.get("facility") or "").strip().lower()

    if not text:
        return jsonify({
            "success": False,
            "error": "Please enter a comment to analyse."
        }), 400

    if facility not in FACILITY_DISPLAY_NAMES:
        facility = "library"

    original_length = len(text)
    is_truncated = False
    if original_length > 1000:
        text = text[:1000]
        is_truncated = True

    try:
        res = pipeline_analyse(text, facility)
        
        # Calculate toxicity score
        tox_score = 0.0
        try:
            out = pipeline_mod._tox([str(text)], truncation=True, max_length=128, function_to_apply="sigmoid")[0]
            tox_score = round(float(max(d["score"] for d in out)), 4)
        except Exception:
            tox_score = 0.99 if res.get("abusive") else 0.01

        is_abusive = bool(res.get("abusive", False))
        display_fac = FACILITY_DISPLAY_NAMES.get(facility, facility.title())

        if is_abusive:
            return jsonify({
                "success": True,
                "abusive": True,
                "toxicity_score": tox_score,
                "toxicity_pct": round(tox_score * 100, 1),
                "facility": facility,
                "display_facility": display_fac,
                "facility_name": display_fac,
                "is_truncated": is_truncated,
                "truncated": is_truncated,
                "original_length": original_length,
                "char_count": original_length,
                "message": f"This comment was flagged as abusive by the Toxic-BERT model (confidence score: {tox_score:.3f}). It has been quarantined and would be excluded from facility ratings.",
                "aspects": []
            })
        else:
            raw_aspects = res.get("aspects", [])
            formatted_aspects = []
            for a in raw_aspects:
                cat = a.get("category", "")
                formatted_aspects.append({
                    "category": cat,
                    "display_category": cat.replace("_", " ").title(),
                    "aspect_term": a.get("aspect_term"),
                    "clause": a.get("clause", "").strip(),
                    "sentiment": a.get("sentiment", "neutral").lower()
                })

            specific_aspects = [a for a in formatted_aspects if a["category"] != "general"]
            final_aspects = specific_aspects if specific_aspects else [a for a in formatted_aspects if a.get("clause")]
            has_topics = len(final_aspects) > 0 and final_aspects[0]["category"] != "general"

            return jsonify({
                "success": True,
                "abusive": False,
                "toxicity_score": tox_score,
                "toxicity_pct": round(tox_score * 100, 1),
                "facility": facility,
                "display_facility": display_fac,
                "facility_name": display_fac,
                "is_truncated": is_truncated,
                "truncated": is_truncated,
                "original_length": original_length,
                "char_count": original_length,
                "aspects": final_aspects,
                "has_topics": has_topics
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"An error occurred during analysis: {str(e)}"
        }), 500

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" Campus Facility Feedback Analysis System - Flask Webapp")
    print(" Running at: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
