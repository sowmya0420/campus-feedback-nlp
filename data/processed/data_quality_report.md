# Campus Facility Feedback NLP Dataset — Data Quality Report

**Generated Date:** 2026-10-19  
**Automated Validation Status:** `PASS`  
**Human Annotation Status:** `PENDING (AWAITING_HUMAN_REVIEW)`  

---

## 1. Executive Summary

This report documents the completed, mathematically reconciled, and validated dataset pipeline for the **NLP-Based Campus Facility Feedback Analysis System**.

| Metric | Target | Actual Count | Compliance Status |
|---|---|---|---|
| Facility Coverage | 8 facilities | 8 facilities | **100% PASS** |
| Batch Count | 16 batches | 16 batches (50 comments each) | **100% PASS** |
| Total Comments | 800 | 800 comments (100 per facility) | **100% PASS** |
| Total Aspect Annotations | Variable | 915 aspect rows | **VALIDATED** |
| Total Abusive Comments | 48 (3 per batch) | 48 comments (6.0%) | **100% PASS** |
| Original Comments Preserved | 538 (100%) | 538 comments (100%) | **100% PASS** |
| Newly Generated Comments | 262 | 262 comments | **100% PASS** |
| Split Ratio (Train / Val / Test) | 70% / 15% / 15% | 560 / 120 / 120 comments | **100% PASS** |
| Split Leakage (ID & Text) | 0 overlap | 0 overlap | **100% PASS** |

---

## 2. Facility & Batch Accounting

Every facility contains exactly two 50-comment batches with exactly 3 abusive comments per batch:

| Facility ID | Display Name | Batch 1 Comments (Abusive) | Batch 2 Comments (Abusive) | Total Comments (Abusive) | Total Aspects |
|---|---|---|---|---|---|
| `hostel_mess` | Hostel Mess | 50 (3) | 50 (3) | 100 (6) | 120 |
| `canteen` | Campus Canteen | 50 (3) | 50 (3) | 100 (6) | 120 |
| `library` | Library | 50 (3) | 50 (3) | 100 (6) | 111 |
| `hostel_rooms` | Hostel Rooms | 50 (3) | 50 (3) | 100 (6) | 109 |
| `labs` | Engineering Labs | 50 (3) | 50 (3) | 100 (6) | 110 |
| `wifi` | Campus Wi-Fi | 50 (3) | 50 (3) | 100 (6) | 109 |
| `transport` | Bus Transport | 50 (3) | 50 (3) | 100 (6) | 114 |
| `classrooms` | Classrooms | 50 (3) | 50 (3) | 100 (6) | 122 |
| **Total** | **All 8 Facilities** | **400 (24)** | **400 (24)** | **800 (48)** | **915** |

---

## 3. Sentiment & Label Distributions

### 3.1 Comment-Level Sentiment Distribution
Derived strictly from aspect sentiments:
- **Negative-only:** 446 comments (55.8%)
- **Positive-only:** 288 comments (36.0%)
- **Mixed:** 51 comments (6.4%)
- **Neutral-only:** 15 comments (1.9%)
- **Unresolved:** 0 comments (0.0%)

### 3.2 Aspect-Level Sentiment Distribution
- **Negative:** 529 aspects (57.8%)
- **Positive:** 362 aspects (39.6%)
- **Neutral:** 24 aspects (2.6%)

---

## 4. Train / Validation / Test Partitions & Zero-Leakage Audit

The dataset was partitioned at the comment level with fixed seed (`SEED = 42`):

| Partition | Comments | Aspects | Abusive Comments | Abusive % | ID Overlap | Text Overlap |
|---|---|---|---|---|---|---|
| **Train** | 560 (70.0%) | 649 | 32 | 5.71% | 0 | 0 |
| **Validation** | 120 (15.0%) | 134 | 8 | 6.67% | 0 | 0 |
| **Test** | 120 (15.0%) | 132 | 8 | 6.67% | 0 | 0 |

### Leakage Verification Results:
- **Comment ID Overlap:** Zero (Train $\cap$ Val = $\emptyset$, Train $\cap$ Test = $\emptyset$, Val $\cap$ Test = $\emptyset$).
- **Normalized Text Overlap:** Zero exact text matches across splits.
- **Near-Duplicate Overlap:** Zero cross-split pairs with Jaccard similarity $\ge 0.85$.
- **Aspect Reconciliation:** 100% of aspect records partition strictly with their parent comment.

---

## 5. External Datasets Status

1. **EduRABSA (Hua et al., 2025, arXiv 2508.17008):**
   - 4,000 train reviews (16,500 aspects) and 2,500 test reviews (10,537 aspects).
   - Domain: Course and faculty evaluation.
   - Converted via `src/adapters.py` into `data/processed/unified_edurabsa_train.csv` and `data/processed/unified_edurabsa_test.csv`.
   - Maintained strictly separate from campus facility feedback.

2. **Jigsaw Toxic Comment Classification:**
   - 159,571 comments from Kaggle toxic comment challenge.
   - Converted via `src/adapters.py` into a balanced 5,000-comment evaluation benchmark (`data/processed/jigsaw_abusive_sample.csv`).
   - Maintained strictly separate from campus facility feedback.

---

## 6. Human Verification & Gold Sample

- **Status:** `AWAITING_HUMAN_REVIEW`
- **Gold Verification File:** `data/processed/gold_to_verify.csv`
- **Sample Selection:** 100 comments sampled strictly from the **TRAINING partition** (never from validation or test).
- **Review Instructions:** Reviewers should inspect each row, verify aspect terms and sentiments, set the `verified` column to `OK` or corrected labels, and save as `gold_test.csv`.
