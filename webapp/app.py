import os
import sys
import re
import requests
import pandas as pd
from flask import Flask, render_template, request, jsonify

# Ensure local offline execution for Hugging Face models
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

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

ALL_FACILITY_KEYS = ["canteen", "classrooms", "hostel_mess", "hostel_rooms", "labs", "library", "transport", "wifi"]

def get_facility_display_name(fac):
    if not fac:
        return ""
    key = str(fac).lower().strip()
    return FACILITY_DISPLAY_NAMES.get(key, key.replace("_", " ").title())

# -----------------------------------------------------------------------------
# Machine Learning Model Pipeline Preloading
# -----------------------------------------------------------------------------
PIPELINE_READY = False
PIPELINE_ERROR = None
pipeline_analyse = None
pipeline_mod = None
extract_aspects_func = None
predict_sentiment_func = None
split_clauses_func = None

print("Loading models (DistilBERT aspect, DistilBERT sentiment, Toxic-BERT)...", flush=True)
try:
    from src.pipeline import analyse as _analyse
    import src.pipeline as _mod
    from src.aspects_hybrid import extract_aspects as _extract_aspects
    from src.sentiment import predict_sentiment as _predict_sentiment
    from src.preprocess import split_clauses as _split_clauses

    pipeline_analyse = _analyse
    pipeline_mod = _mod
    extract_aspects_func = _extract_aspects
    predict_sentiment_func = _predict_sentiment
    split_clauses_func = _split_clauses

    # Warm up with a simple sentence to load model weights into memory once
    _ = pipeline_analyse("campus feedback system test", "library")
    PIPELINE_READY = True
    print("Models loaded successfully and ready for inference.", flush=True)
except Exception as e:
    PIPELINE_ERROR = str(e)
    print(f"Warning: Models failed to load on startup: {e}", flush=True)

# -----------------------------------------------------------------------------
# Ollama Local AI Model Startup Check and Warm-up
# -----------------------------------------------------------------------------
OLLAMA_AVAILABLE = False
OLLAMA_MODEL = "llama3.1"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"

print("Checking Ollama status at http://localhost:11434...", flush=True)
try:
    r = requests.get(OLLAMA_TAGS_URL, timeout=3)
    if r.status_code == 200:
        models = r.json().get("models", [])
        names = [m.get("name", "") for m in models]
        if any(OLLAMA_MODEL in name for name in names):
            print(f"Ollama is running and '{OLLAMA_MODEL}' is ready.", flush=True)
            print(f"Warming up '{OLLAMA_MODEL}' for live demo summaries...", flush=True)
            warm = requests.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": "Hi", "stream": False},
                timeout=90
            )
            if warm.status_code == 200:
                OLLAMA_AVAILABLE = True
                print(f"Ollama model '{OLLAMA_MODEL}' warmed up and ready for inference.", flush=True)
            else:
                print(f"Ollama warm-up returned status {warm.status_code}. Using auto-generated fallback summaries.", flush=True)
        else:
            print(f"Ollama is running, but '{OLLAMA_MODEL}' was not found in installed models. Using auto-generated fallback summaries.", flush=True)
    else:
        print(f"Ollama returned status {r.status_code}. Using auto-generated fallback summaries.", flush=True)
except Exception as e:
    print(f"Ollama is not running (error: {e}). Live demo will use auto-generated fallback summaries.", flush=True)

# -----------------------------------------------------------------------------
# Cached Data Loaders
# -----------------------------------------------------------------------------
def load_ratings():
    path = os.path.join(DATA_OUT, "ratings.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["facility", "category", "rating", "mentions", "positive", "neutral", "negative", "negative_share", "display_facility"])
    df = pd.read_csv(path)
    df["display_facility"] = df["facility"].apply(get_facility_display_name)
    return df

def load_issues():
    path = os.path.join(DATA_OUT, "issues.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["facility", "category", "rating", "mentions", "positive", "neutral", "negative", "negative_share", "display_facility"])
    df = pd.read_csv(path)
    df["display_facility"] = df["facility"].apply(get_facility_display_name)
    return df

def load_summaries():
    path = os.path.join(DATA_OUT, "summaries.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["facility", "summary", "display_facility"])
    df = pd.read_csv(path)
    df["display_facility"] = df["facility"].apply(get_facility_display_name)
    return df

def load_predictions():
    path = os.path.join(DATA_OUT, "predictions.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["id", "facility", "text", "abusive", "category", "sentiment", "display_facility"])
    df = pd.read_csv(path)
    df["display_facility"] = df["facility"].apply(get_facility_display_name)
    return df

@app.context_processor
def inject_global_data():
    return {
        "project_name": "Campus Facility Feedback Analysis System",
        "short_title": "Campus Feedback",
        "team_label": "Final Year NLP Project"
    }

# -----------------------------------------------------------------------------
# Clause Facility Routing Rules (For "All facilities" mode)
# -----------------------------------------------------------------------------
def detect_clause_facility(clause):
    """
    Detects which facility a single clause specifically belongs to.
    Wi-Fi words win in ambiguous hostel clauses.
    Hostel is disambiguated by mess vs room words.
    Returns facility key ('canteen', 'library', etc.) or None if unstated.
    """
    cl = clause.lower()

    # 1. Wi-Fi words win if combined with hostel or standalone
    if re.search(r"\b(wifi|wi-fi|internet|broadband|hotspot)\b", cl):
        return "wifi"

    # 2. Specific facility keywords
    if re.search(r"\b(library|reading room|librarian|librarians)\b", cl):
        return "library"
    if re.search(r"\b(canteen|cafeteria)\b", cl):
        return "canteen"
    if re.search(r"\b(classroom|classrooms|lecture hall|lecture halls|class room|class rooms)\b", cl):
        return "classrooms"
    if re.search(r"\b(bus|buses|transport|driver|drivers|conductor|college bus)\b", cl):
        return "transport"
    if re.search(r"\b(lab|labs|laboratory|laboratories)\b", cl):
        return "labs"
    if re.search(r"\b(mess|dining hall)\b", cl):
        return "hostel_mess"

    # 3. Hostel disambiguation rule
    if re.search(r"\b(hostel|hostels)\b", cl):
        # Wi-Fi words
        if re.search(r"\b(disconnect|disconnects|disconnecting|signal|speed|router)\b", cl):
            return "wifi"
        # Mess words
        if re.search(r"\b(food|meal|meals|lunch|dinner|breakfast|sambar|rasam|cook|cooks)\b", cl):
            return "hostel_mess"
        # Room words
        if re.search(r"\b(room|rooms|bed|beds|cot|bathroom|bathrooms|washroom|toilet|toilets|geyser|plumber)\b", cl):
            return "hostel_rooms"
        # Ambiguous hostel alone
        return None

    return None

# -----------------------------------------------------------------------------
# 1. HOME ROUTE
# -----------------------------------------------------------------------------
@app.route("/")
def home():
    ratings_df = load_ratings()
    pred_df = load_predictions()

    ov = ratings_df[ratings_df["category"] == "OVERALL"]

    total_comments = int(pred_df["id"].nunique())
    facility_count = int(ov["facility"].nunique())
    avg_rating = round(float(ov["rating"].mean()), 2)
    flagged_count = int(pred_df[pred_df["abusive"] == True]["id"].nunique())

    ov_sorted = ov.sort_values("rating", ascending=False)
    best_row = ov_sorted.iloc[0]
    worst_row = ov_sorted.iloc[-1]

    stats = {
        "total_comments": total_comments,
        "facility_count": facility_count,
        "avg_rating": avg_rating,
        "flagged_count": flagged_count,
        "best_facility": best_row["display_facility"],
        "best_rating": round(float(best_row["rating"]), 2),
        "worst_facility": worst_row["display_facility"],
        "worst_rating": round(float(worst_row["rating"]), 2),
    }

    return render_template("home.html", stats=stats, active_page="home")

# -----------------------------------------------------------------------------
# 2. LIVE DEMO ROUTE
# -----------------------------------------------------------------------------
@app.route("/demo")
@app.route("/submit")
def demo():
    facilities = [
        {"id": fac, "name": FACILITY_DISPLAY_NAMES[fac]}
        for fac in sorted(FACILITY_DISPLAY_NAMES.keys(), key=lambda k: FACILITY_DISPLAY_NAMES[k])
    ]
    return render_template(
        "demo.html",
        active_page="demo",
        facilities=facilities,
        models_ready=PIPELINE_READY,
        model_error=PIPELINE_ERROR,
        ollama_ready=OLLAMA_AVAILABLE
    )

# -----------------------------------------------------------------------------
# 3. FACILITY EXPLORER ROUTE
# -----------------------------------------------------------------------------
@app.route("/explorer")
def explorer():
    ratings_df = load_ratings()
    issues_df = load_issues()
    pred_df = load_predictions()

    ov = ratings_df[ratings_df["category"] == "OVERALL"].copy()
    ov["rating"] = ov["rating"].round(2)
    ov = ov.sort_values("rating", ascending=False)

    facilities_list = []
    for _, row in ov.iterrows():
        fac_key = row["facility"]
        fac_issues = issues_df[issues_df["facility"] == fac_key]
        top_issue = fac_issues.iloc[0]["category"] if not fac_issues.empty else "No major issue"
        issue_cnt = len(fac_issues)
        comment_count = int(pred_df[pred_df["facility"] == fac_key]["id"].nunique())

        fac_aspects = ratings_df[(ratings_df["facility"] == fac_key) & (ratings_df["category"] != "OVERALL")]
        aspects_list = []
        for _, ar in fac_aspects.iterrows():
            aspects_list.append({
                "category": ar["category"].replace("_", " ").title(),
                "rating": round(float(ar["rating"]), 2),
                "mentions": int(ar["mentions"])
            })
        aspects_list.sort(key=lambda x: x["rating"], reverse=True)

        facilities_list.append({
            "id": fac_key,
            "name": row["display_facility"],
            "rating": float(row["rating"]),
            "top_issue": top_issue.title(),
            "issues_count": issue_cnt,
            "comments_count": comment_count,
            "aspects": aspects_list,
            "status": "Good" if row["rating"] >= 2.6 else ("Moderate" if row["rating"] >= 2.45 else "Needs Improvement")
        })

    return render_template("explorer.html", facilities=facilities_list, active_page="explorer")

# -----------------------------------------------------------------------------
# 4. ASPECT-WISE RATINGS ROUTE
# -----------------------------------------------------------------------------
@app.route("/ratings")
def ratings():
    df = load_ratings()
    ov = df[df["category"] == "OVERALL"].sort_values("rating", ascending=False)
    facilities_list = [
        {"id": row["facility"], "name": row["display_facility"], "rating": round(float(row["rating"]), 2)}
        for _, row in ov.iterrows()
    ]
    topics_list = sorted([c for c in df["category"].unique() if c != "OVERALL"])
    campus_avg = round(float(ov["rating"].mean()), 2)

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

# -----------------------------------------------------------------------------
# 5. RECURRING ISSUES ROUTE
# -----------------------------------------------------------------------------
@app.route("/issues")
def issues():
    issues_df = load_issues()
    pred_df = load_predictions()

    clean_pred = pred_df[(~pred_df["abusive"]) & (pred_df["sentiment"] == "negative")].copy()

    facilities_list = [
        {"id": fac, "name": FACILITY_DISPLAY_NAMES[fac]}
        for fac in sorted(FACILITY_DISPLAY_NAMES.keys(), key=lambda k: FACILITY_DISPLAY_NAMES[k])
    ]

    min_neg_share = round(float(issues_df["negative_share"].min() * 100), 1)
    max_neg_share = round(float(issues_df["negative_share"].max() * 100), 1)

    issues_records = []
    for _, row in issues_df.iterrows():
        fac = row["facility"]
        cat = row["category"]
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

# -----------------------------------------------------------------------------
# 6. FACILITY BRIEFS ROUTE
# -----------------------------------------------------------------------------
@app.route("/briefs")
@app.route("/summaries")
def briefs():
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

        ov_row = ov[ov["facility"] == fac_key]
        rating_val = round(float(ov_row.iloc[0]["rating"]), 2) if not ov_row.empty else 0.0

        comments_cnt = int(pred_df[pred_df["facility"] == fac_key]["id"].nunique())

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
        active_page="briefs",
        facilities=facility_summaries
    )

# -----------------------------------------------------------------------------
# 7. ABUSIVE CONTENT ROUTE
# -----------------------------------------------------------------------------
@app.route("/abusive")
@app.route("/flagged")
def abusive():
    pred_df = load_predictions()

    tox_path = os.path.join(DATA_OUT, "toxicity_bert_campus.csv")
    tox_df = pd.read_csv(tox_path) if os.path.exists(tox_path) else pd.DataFrame()

    flagged_df = pred_df[pred_df["abusive"] == True][["id", "facility", "text", "display_facility"]].drop_duplicates(subset=["id"]).copy()

    if not tox_df.empty and "bert_score" in tox_df.columns:
        flagged_df = pd.merge(flagged_df, tox_df[["id", "bert_score"]], on="id", how="left")
    else:
        flagged_df["bert_score"] = 0.5

    total_comments = int(pred_df["id"].nunique())
    flagged_count = int(len(flagged_df))
    moderation_rate = round((flagged_count / total_comments) * 100, 1)

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

    records.sort(key=lambda x: x["bert_score"], reverse=True)

    return render_template(
        "flagged.html",
        active_page="abusive",
        total_comments=total_comments,
        flagged_count=flagged_count,
        moderation_rate=moderation_rate,
        facility_breakdown=facility_breakdown,
        flagged_comments=records
    )

# -----------------------------------------------------------------------------
# API: Real-time Analysis (One row per aspect group, Carry-over, Disambiguation)
# -----------------------------------------------------------------------------
@app.route("/api/analyse", methods=["POST"])
def api_analyse():
    if not PIPELINE_READY:
        return jsonify({
            "success": False,
            "error": "Machine learning models could not be loaded into memory: " + str(PIPELINE_ERROR or "Check model files in models/.")
        }), 503

    data = request.get_json(silent=True) or request.form
    text = (data.get("text") or "").strip()
    selected_facility = (data.get("facility") or "all").strip().lower()

    if not text:
        return jsonify({
            "success": False,
            "error": "Please enter a comment to analyse."
        }), 400

    original_length = len(text)
    is_truncated = False
    if original_length > 1000:
        text = text[:1000]
        is_truncated = True

    try:
        # Step 1: Run Toxic-BERT abusive content check ONCE per comment
        tox_score = 0.0
        try:
            out = pipeline_mod._tox([str(text)], truncation=True, max_length=128, function_to_apply="sigmoid")[0]
            tox_score = round(float(max(d["score"] for d in out)), 4)
        except Exception:
            tox_score = 0.01

        is_abusive = bool(tox_score >= 0.5)

        if is_abusive:
            return jsonify({
                "success": True,
                "abusive": True,
                "toxicity_score": tox_score,
                "toxicity_score_display": f"{tox_score:.3f}",
                "toxicity_pct": round(tox_score * 100, 1),
                "is_truncated": is_truncated,
                "char_count": original_length,
                "message": "This comment was flagged as abusive by the Toxic-BERT model and would be excluded from facility ratings.",
                "aspect_groups": [],
                "has_topics": False
            })

        # Step 2: Extract Aspects and Sentiments
        raw_clauses = split_clauses_func(text)
        clauses = []
        for c in raw_clauses:
            parts = re.split(r"\b(?:and|also|plus)\b", c, flags=re.IGNORECASE)
            for p in parts:
                p = p.strip()
                if p:
                    clauses.append(p)
        raw_aspects = []

        if selected_facility != "all" and selected_facility in FACILITY_DISPLAY_NAMES:
            # Single-facility mode: entire comment is analyzed for this facility
            for c in clauses:
                found = extract_aspects_func(c, selected_facility)
                for a in found:
                    if a["category"] != "general":
                        sen = predict_sentiment_func(a["clause"], a["aspect_term"] or a["category"])
                        raw_aspects.append({
                            "facility": selected_facility,
                            "facility_display": FACILITY_DISPLAY_NAMES[selected_facility],
                            "facility_note": None,
                            "category": a["category"],
                            "aspect_term": a["aspect_term"],
                            "clause": a["clause"],
                            "sentiment": sen
                        })
        else:
            # "All facilities" mode with Carry-Over, No Silent Guessing, and Hostel Disambiguation
            curr_facility = None
            for c in clauses:
                det = detect_clause_facility(c)
                if det:
                    curr_facility = det
                    clause_fac = det
                elif curr_facility:
                    clause_fac = curr_facility
                else:
                    clause_fac = None

                if clause_fac:
                    found = extract_aspects_func(c, clause_fac)
                    for a in found:
                        if a["category"] != "general":
                            sen = predict_sentiment_func(a["clause"], a["aspect_term"] or a["category"])
                            raw_aspects.append({
                                "facility": clause_fac,
                                "facility_display": FACILITY_DISPLAY_NAMES[clause_fac],
                                "facility_note": None,
                                "category": a["category"],
                                "aspect_term": a["aspect_term"],
                                "clause": a["clause"],
                                "sentiment": sen
                            })
                else:
                    # No facility stated and no carry-over (Rule 2)
                    # Check if core feedback/aspect terms exist
                    core_feedback_words = re.search(
                        r"\b(food|taste|tasty|price|prices|cost|expensive|cheap|hygiene|clean|dirty|wait|waiting|queue|line|staff|polite|rude|seat|seating|ac|fan|fans|noise|loud|quiet|speed|slow|fast|bus|water|book)\b",
                        c.lower()
                    )

                    if not core_feedback_words:
                        # Isolated non-feedback items without facility context
                        continue

                    fac_matches = {}
                    for f in ALL_FACILITY_KEYS:
                        asp = [a for a in extract_aspects_func(c, f) if a["category"] != "general"]
                        if asp:
                            fac_matches[f] = asp

                    if fac_matches:
                        cats = set()
                        for f, asps in fac_matches.items():
                            for a in asps:
                                cats.add(a["category"])

                        for cat in cats:
                            matching_facs = [
                                FACILITY_DISPLAY_NAMES[f]
                                for f, asps in fac_matches.items()
                                if any(a["category"] == cat for a in asps)
                            ]
                            note = f"fits {', '.join(matching_facs)}" if len(matching_facs) > 1 else None
                            sen = predict_sentiment_func(c, cat)

                            raw_aspects.append({
                                "facility": "none",
                                "facility_display": "Facility not stated",
                                "facility_note": note,
                                "category": cat,
                                "aspect_term": None,
                                "clause": c,
                                "sentiment": sen
                            })

        # Step 3: Group detected rows by (facility, aspect)
        grouped = {}
        for item in raw_aspects:
            key = (item["facility"], item["category"])
            if key not in grouped:
                grouped[key] = {
                    "facility": item["facility"],
                    "facility_display": item["facility_display"],
                    "facility_note": item["facility_note"],
                    "category": item["category"],
                    "display_category": item["category"].replace("_", " ").title(),
                    "evidence": [],
                    "sentiments": []
                }
            clause_clean = item["clause"].strip().capitalize()
            if clause_clean and clause_clean not in grouped[key]["evidence"]:
                grouped[key]["evidence"].append(clause_clean)
            grouped[key]["sentiments"].append(item["sentiment"])

        result_groups = []
        for key, g in grouped.items():
            sens = g["sentiments"]
            pos = sens.count("positive")
            neu = sens.count("neutral")
            neg = sens.count("negative")
            n = len(sens)

            # Sentiment per group: if all agree, show that sentiment; if disagree, show Mixed in amber
            if pos == n:
                group_sentiment = "positive"
                badge_label = "Positive"
            elif neu == n:
                group_sentiment = "neutral"
                badge_label = "Neutral"
            elif neg == n:
                group_sentiment = "negative"
                badge_label = "Negative"
            else:
                group_sentiment = "mixed"
                badge_label = "Mixed"

            # Stars per group: project formula 1 + 4*(pos + 0.5*neu)/n with half-up rounding
            score = 1.0 + 4.0 * (pos + 0.5 * neu) / n
            stars = int(score + 0.5)
            stars = max(1, min(5, stars))

            result_groups.append({
                "facility": g["facility"],
                "facility_display": g["facility_display"],
                "facility_note": g["facility_note"],
                "category": g["category"],
                "display_category": g["display_category"],
                "evidence": " / ".join(g["evidence"]),
                "sentiment": group_sentiment,
                "badge_label": badge_label,
                "score": round(score, 2),
                "stars": stars
            })

        # Order rows grouped by facility
        fac_order = {f: i for i, f in enumerate(ALL_FACILITY_KEYS)}
        fac_order["none"] = 999
        result_groups.sort(key=lambda x: (fac_order.get(x["facility"], 999), x["display_category"]))

        return jsonify({
            "success": True,
            "abusive": False,
            "toxicity_score": tox_score,
            "toxicity_score_display": f"{tox_score:.3f}",
            "toxicity_pct": round(tox_score * 100, 1),
            "is_all_mode": (selected_facility == "all"),
            "is_truncated": is_truncated,
            "char_count": original_length,
            "aspect_groups": result_groups,
            "has_topics": len(result_groups) > 0
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"An error occurred during analysis: {str(e)}"
        }), 500

# -----------------------------------------------------------------------------
# API: Live Summary Generation (Given grouped aspects: facility, aspect, sentiment only)
# -----------------------------------------------------------------------------
@app.route("/api/summarize-live", methods=["POST"])
def api_summarize_live():
    data = request.get_json(silent=True) or request.form
    text = (data.get("text") or "").strip()
    aspect_groups = data.get("aspect_groups") or []
    is_abusive = bool(data.get("abusive", False))

    if is_abusive or not aspect_groups:
        return jsonify({
            "success": True,
            "summary": None,
            "label": None,
            "source": "none"
        })

    summary_text = None
    source = "fallback"
    label = "Auto-generated from detected aspects"

    if OLLAMA_AVAILABLE:
        try:
            # Format grouped aspects: facility, aspect name, and sentiment only
            asp_lines = ", ".join(
                f"{a.get('facility_display')}: {a.get('display_category')} ({a.get('sentiment')})"
                for a in aspect_groups
            )

            prompt = f"""You are summarizing student feedback about campus facilities.

Detected aspects and sentiment:
{asp_lines}

Instructions:
- Write exactly 2 or 3 plain, direct sentences summarizing this student feedback.
- Mention ONLY the facilities and aspects listed above ({asp_lines}). Do not mention any other facility or topic.
- Do NOT include any numbers, ratings, percentages, or counts.
- Do NOT invent causes, background facts, or recommendations.
- Keep the wording simple and objective.
- Return ONLY the summary sentences, nothing else."""

            reply = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2},
                },
                timeout=60,
            )
            if reply.status_code == 200:
                resp_json = reply.json()
                t = resp_json.get("response", "").strip()
                if t:
                    summary_text = t
                    source = "ollama"
                    label = "AI summary (local model)"
        except Exception as e:
            print(f"Ollama live summary request failed or timed out: {e}", flush=True)
            summary_text = None

    if not summary_text:
        # Fallback multi-facility summary built strictly from detected groups
        pos_items = [f"{a['display_category']} in {a['facility_display']}" for a in aspect_groups if a['sentiment'] == 'positive']
        neg_items = [f"{a['display_category']} in {a['facility_display']}" for a in aspect_groups if a['sentiment'] == 'negative']
        mixed_items = [f"{a['display_category']} in {a['facility_display']}" for a in aspect_groups if a['sentiment'] in ('neutral', 'mixed')]

        sentences = []
        if pos_items:
            sentences.append(f"Positive feedback was recorded for {', '.join(pos_items)}.")
        if neg_items:
            sentences.append(f"Student concerns were noted regarding {', '.join(neg_items)}.")
        if mixed_items:
            sentences.append(f"Neutral or mixed observations were reported for {', '.join(mixed_items)}.")

        summary_text = " ".join(sentences) if sentences else "Student feedback was evaluated across detected campus facilities."
        source = "fallback"
        label = "Auto-generated from detected aspects"

    return jsonify({
        "success": True,
        "summary": summary_text,
        "source": source,
        "label": label
    })

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" Campus Facility Feedback Analysis System - Dark Dashboard")
    print(" Running at: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
