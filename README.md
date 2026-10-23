# NLP-Based Campus Facility Feedback Analysis System

An NLP research and data engineering platform designed to analyse student feedback across campus facilities. The system is designed to support:
1. **Text preprocessing and normalization** (handling informal Tamil-English/Tanglish slang, abbreviations, and typos).
2. **Facility-related aspect extraction** (identifying specific components such as equipment, food, seating, etc.).
3. **Aspect-Based Sentiment Analysis (ABSA)** (classifying aspect polarities as positive, negative, or neutral).
4. **Aspect-wise facility ratings** (aggregating sentiment to grade facilities).
5. **Recurring issue identification** (clustering and tracking chronic complaints).
6. **AI-based summaries of aggregated feedback** (generating structured executive facility briefs).
7. **Abusive-content detection** (detecting profanity, insults, and harassment).

---

## 1. Directory Structure

```
campus-feedback-nlp/
├── data/
│   ├── raw_backup_original/            # Immutable backup of original 538 raw comments
│   ├── processed_backup_original/      # Immutable backup of initial processed files
│   ├── raw/                            # 16 batch files + 8 combined facility files (800 comments total)
│   │   ├── <facility>_1.json           # Batch 1 (50 comments, 3 abusive)
│   │   ├── <facility>_2.json           # Batch 2 (50 comments, 3 abusive)
│   │   └── <facility>.json             # Combined facility file (100 comments, 6 abusive)
│   ├── processed/                      # Canonical processed CSVs, splits, and reports
│   │   ├── campus_feedback.csv         # Full 800 comments with metadata & derived sentiment
│   │   ├── campus_aspects.csv          # 915 flattened aspect rows linked by parent ID
│   │   ├── train_comments.csv          # Train partition (560 comments, 70%)
│   │   ├── validation_comments.csv     # Validation partition (120 comments, 15%)
│   │   ├── test_comments.csv           # Test partition (120 comments, 15%)
│   │   ├── train_aspects.csv           # 649 aspects for training
│   │   ├── validation_aspects.csv      # 134 aspects for validation
│   │   ├── test_aspects.csv            # 132 aspects for testing
│   │   ├── gold_to_verify.csv          # 100-comment human review sample (sampled strictly from Train)
│   │   ├── dataset_manifest.json       # Checksums, schemas, provenance, and file inventory
│   │   ├── data_quality_report.json    # Machine-readable automated validation audit
│   │   ├── data_quality_report.md      # Human-readable quality assurance report
│   │   ├── label_distribution.csv      # Facility and global aspect/comment label frequencies
│   │   ├── unresolved_annotations.csv  # Implied aspects (null terms) and edge annotations
│   │   ├── unified_edurabsa_train.csv  # EduRABSA train set (16,500 aspect rows)
│   │   ├── unified_edurabsa_test.csv   # EduRABSA test set (10,537 aspect rows)
│   │   ├── unified_synthetic.csv       # Standardized schema for synthetic campus data (915 rows)
│   │   └── jigsaw_abusive_sample.csv   # Balanced Jigsaw benchmark sample (5,000 comments)
│   └── external/
│       ├── edurabsa/                   # EduRABSA academic ABSA dataset (train/test jsonl)
│       └── jigsaw/                     # Jigsaw Toxic Comment Classification Challenge (train.csv)
├── src/
│   ├── data_definitions.py             # Schema, categories whitelist, personas constants
│   ├── validate_dataset.py             # Deterministic 18-rule validation test suite
│   ├── merge_campus_data.py            # Raw JSON ingestion, normalization, and flattening
│   ├── split_data.py                   # Comment-level 70/15/15 stratified partitioner with zero leakage
│   ├── adapters.py                     # Format converters for EduRABSA and Jigsaw
│   ├── generate_reports.py             # Generates manifest, distributions, and quality reports
│   └── run_pipeline.py                 # Master single-command pipeline runner
├── requirements.txt                    # Minimal data pipeline dependencies
└── README.md                           # Comprehensive documentation and reproducibility guide
```

---

## 2. Facility Coverage and Allowed Aspect Categories

The system covers **eight facilities**, each governed by an explicit whitelist of allowed aspect categories. Category cross-contamination across facilities is prohibited:

| Facility ID | Facility Name | Allowed Aspect Categories |
|---|---|---|
| `hostel_mess` | Hostel Mess | `food quality`, `price`, `hygiene`, `waiting time`, `seating`, `staff behavior`, `quantity`, `variety` |
| `canteen` | Campus Canteen / Food Court | `food quality`, `price`, `hygiene`, `waiting time`, `seating`, `staff behavior`, `quantity`, `variety` |
| `library` | Central Library | `book availability`, `seating`, `silence`, `opening hours`, `staff behavior`, `cleanliness`, `ac/temperature`, `digital resources` |
| `hostel_rooms` | Hostel Rooms & Living Facilities | `cleanliness`, `water supply`, `electricity`, `maintenance`, `room size`, `safety`, `laundry`, `noise` |
| `labs` | Computer & Engineering Labs | `equipment condition`, `system speed`, `software availability`, `lab staff`, `lab timings`, `cleanliness`, `space` |
| `wifi` | Campus Wi-Fi & Internet | `speed`, `connectivity`, `coverage`, `login issues`, `reliability`, `bandwidth limit` |
| `transport` | College Bus Transport | `punctuality`, `crowding`, `driver behavior`, `route coverage`, `bus condition`, `safety`, `fare` |
| `classrooms` | Classrooms & Lecture Halls | `ac/temperature`, `seating`, `projector/av`, `cleanliness`, `lighting`, `noise` |

---

## 3. Dataset Provenance and Reconstruction

### 3.1 Provenance Accounting
- **Original Recovered (538 comments, 100% preserved):** All 538 comments originally present in `data/raw/` (canteen: 84, hostel_mess: 94, hostel_rooms: 76, labs: 74, library: 80, transport: 64, wifi: 66) were mathematically reconciled into Batch 1 and partial Batch 2 without dropping or modifying a single comment text, aspect label, or abusive flag.
- **Newly Generated (262 comments):** Synthesized to complete partial Batch 2 (162 comments) and generate the missing `classrooms` facility (100 comments across B1 and B2).
- **Total Dataset:** Exactly 800 comments across 16 batches (50 comments per batch, exactly 3 abusive per batch).

### 3.2 Personas
- **Batch 1 Personas:** `first-year hosteller`, `second-year day scholar`, `final-year student`, `girls' hostel resident`, `outstation student`.
- **Batch 2 Personas:** `placement-focused student`, `club member`, `backlog student`, `third-year hosteller`, `faculty-project student`.

---

## 4. Annotation Schema and Sentiment Taxonomy

### 4.1 Raw JSON Comment Schema
```json
{
  "id": "C_CAN_01_001",
  "legacy_id": "C0001",
  "facility": "canteen",
  "batch": 1,
  "persona": "first-year hosteller",
  "persona_status": "assigned_for_balance",
  "text": "samosa is crispy and cheap, best snack here",
  "aspects": [
    {"aspect_term": "samosa", "category": "food quality", "sentiment": "positive"},
    {"aspect_term": "cheap", "category": "price", "sentiment": "positive"}
  ],
  "abusive": false,
  "source_type": "synthetic",
  "provenance": "original_recovered"
}
```

### 4.2 Explicit Comment-Level Sentiment Derivation
Let $S_c$ be the set of aspect sentiment polarities in comment $c$:
- **Mixed:** $\text{'positive'} \in S_c \ \land \ \text{'negative'} \in S_c$.
- **Positive:** $\text{'positive'} \in S_c \ \land \ \text{'negative'} \notin S_c$.
- **Negative:** $\text{'negative'} \in S_c \ \land \ \text{'positive'} \notin S_c$.
- **Neutral:** $S_c = \{\text{'neutral'}\}$.
- **Unresolved:** $|c.\text{aspects}| = 0$ (e.g. pure insults with no specific facility aspect opinion).

---

## 5. Train / Validation / Test Methodology & Leakage Prevention

The dataset is partitioned strictly at the **comment level** using fixed random seed `SEED = 42`:
- **Training (70%):** 560 comments (649 aspects, 32 abusive comments). Exactly 70 comments per facility.
- **Validation (15%):** 120 comments (134 aspects, 8 abusive comments). Exactly 15 comments per facility.
- **Test (15%):** 120 comments (132 aspects, 8 abusive comments). Exactly 15 comments per facility.

### Leakage Verification Suite
- **Comment ID Overlap:** Zero (Train $\cap$ Val = $\emptyset$, Train $\cap$ Test = $\emptyset$, Val $\cap$ Test = $\emptyset$).
- **Normalized Text Overlap:** Zero exact text matches across splits.
- **Near-Duplicate Overlap:** Zero cross-split pairs with token Jaccard similarity $\ge 0.85$.
- **Aspect Partitioning:** 100% of aspect records partition strictly with their parent comment ID.
- **Gold Verification Sample (`gold_to_verify.csv`):** Sampled strictly from the **TRAINING partition** (100 comments). Test data is strictly held out.

---

## 6. How to Reproduce and Validate the Dataset Pipeline

### 6.1 Setup Environment
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 6.2 Execute Entire Pipeline in One Command
```powershell
python src/run_pipeline.py
```
This automatically runs:
1. `python src/validate_dataset.py` (pre-validation)
2. `python src/merge_campus_data.py` (builds `campus_feedback.csv` and `campus_aspects.csv`)
3. `python src/split_data.py` (produces 70/15/15 partitions and `gold_to_verify.csv`)
4. `python src/adapters.py` (processes EduRABSA and Jigsaw external datasets)
5. `python src/generate_reports.py` (generates manifest, quality reports, label distributions)
6. `python src/validate_dataset.py` (post-validation check)

---

## 7. Known Limitations and Review Tasks

1. **Synthetic Data Limitations:** The campus dataset was generated using an LLM to simulate Indian engineering college students in Tamil Nadu with ~40% Tanglish phrases. While linguistically diverse, labels represent synthetic annotations.
2. **Human Annotation Review Status:** Currently `AWAITING_HUMAN_REVIEW`. Reviewers should audit `data/processed/gold_to_verify.csv`, fill in the `verified` column, and save it as `gold_test.csv`.
3. **Implied Aspects Queue:** Four records with implied aspect terms (`aspect_term: null`) are documented in `data/processed/unresolved_annotations.csv` for human reviewer attention.

---

## 8. Starting Model Training (Next Steps)

Once human review of the gold sample is completed, model training can proceed:
1. **Aspect Extraction & Category Classification:** Train token classification models (e.g. DeBERTa-v3, IndicBERT) or sequence-to-sequence prompt models on `train_aspects.csv`, evaluate on `validation_aspects.csv`, and test on `test_aspects.csv`.
2. **Aspect-Based Sentiment Analysis (ABSA):** Train sentiment classifiers predicting positive, negative, or neutral for extracted (aspect_term, category) pairs. Use EduRABSA (`unified_edurabsa_train.csv`) for domain pretraining if beneficial.
3. **Abusive Content Detection:** Train binary classifiers (`abusive: true/false`) on `train_comments.csv`, using `data/processed/jigsaw_abusive_sample.csv` for out-of-domain benchmark evaluation.
