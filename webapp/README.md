# Campus Facility Feedback Analysis System - Web Application

This web application is the presentation interface for the final-year NLP project on campus facility feedback. It displays aspect-based sentiment analysis, recurring issue detection, executive summaries, and toxicity moderation across eight campus facilities. It also includes an interactive testing page to evaluate new student feedback comments in real time using the project's trained models.

## How to Start

Run this command in PowerShell from the project root folder:

```powershell
.\venv\Scripts\python.exe webapp/app.py
```

Then open your browser and navigate to:

```text
http://127.0.0.1:5000
```

## Pages in the Website

1. Home (/): Executive overview showing campus-wide KPI metrics, facility rating comparisons, the six-step pipeline workflow, and an interactive facility inspector.
2. Ratings (/ratings): Interactive scorecards, benchmark comparisons, and sortable tables for overall facility scores and topic-level sentiment ratings.
3. Recurring Issues (/issues): Severe complaint areas per facility with a dynamic negative-share threshold slider and expandable verified student quotes.
4. Summaries (/summaries): Facility presentation cards displaying written narrative summaries, main complaint areas, and a side-by-side comparison mode.
5. Flagged Comments (/flagged): Moderation log displaying all 49 quarantined abusive comments with Toxic-BERT confidence scores and safe inline preview toggles.
6. Submit Feedback (/submit): Real-time testing form to evaluate custom feedback comments with aspect extraction, sentiment classification, and toxicity checking.

## Data Access and Storage Rules

The web application accesses files in data/outputs/ in read-only mode:
- data/outputs/ratings.csv
- data/outputs/issues.csv
- data/outputs/summaries.csv
- data/outputs/predictions.csv
- data/outputs/toxicity_bert_campus.csv

The web application never writes, creates, edits, or deletes any file in data/outputs/ or anywhere else in the project. Feedback submitted on the live form is processed strictly in memory and is discarded after analysis.

## Required Packages

- Flask (installed in the project virtual environment)
- Existing project packages: torch, transformers, pandas, joblib, vaderSentiment

All fonts, icons, and JavaScript libraries (Chart.js v4.4.7) are stored locally in webapp/static/ so the application runs completely offline without an internet connection.

## Known Limits

- The hybrid aspect finder combines keyword matching with a DistilBERT multilabel classifier; on occasion, the model can add an extra topic that was not explicitly mentioned in the comment text.
- The sentiment model uses lexicons and trained features where certain informational words carry positive valence (for example, the word "open" has a positive weight), which can cause neutral factual statements (such as library operating hours) to be labeled as positive rather than neutral.
