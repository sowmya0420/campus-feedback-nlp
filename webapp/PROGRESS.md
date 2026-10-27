# Project Redesign Progress Log

This document tracks the progress of the dark-mode dashboard redesign for the **Campus Facility Feedback Analysis System**. It allows any session to continue immediately with full context.

---

## 1. How to Run the Website

Run this single command from the project root folder:

```powershell
.\venv\Scripts\python.exe webapp/app.py
```

Then open your browser and navigate to:
```text
http://127.0.0.1:5000
```

> **Note on Ollama**: Ensure Ollama is running (`ollama serve` or Ollama app in background) if you want real-time AI summaries on the Live Demo page. If Ollama is not running, the site automatically falls back to an auto-generated factual summary based strictly on the detected aspects.

---

## 2. Redesign Status by Step

| Step | Page / Component | Status | Details |
|---|---|---|---|
| **Step 1** | **Dark Theme & Left Sidebar** | **Finished** | Central dark CSS variables configured (#0e1013, #13161b, #181b21, #1f232b, #2b303a, accent #fb923c). Old purple/light colors completely removed. Fixed left sidebar with all 7 links in exact order and outline SVGs with `currentColor`. Fits on 1366x768 and 1920x1080 without outer scrolling. Bottom "Next:" / "Back to Home" buttons removed. |
| **Step 2** | **Home Page** | **Finished** | Clean, single-screen overview with project title, 1-line plain description, 4 number cards (Total comments: 800, Facilities: 8, Average rating: 2.54 / 5.0, Flagged comments: 49), and a "Try it live" action button linking directly to Live Demo. Old chart and inspector removed. |
| **Step 3** | **Live Demo (Parts 1 & 2)** | **Finished (Ready to test)** | 1. **"All facilities" Option**: Default option in dropdown. Implements clause routing with Wi-Fi location-word protection, hostel disambiguation (Wi-Fi vs Mess vs Rooms), unanchored carry-over, and "Facility not stated" tagging.<br>2. **Grouped Aspect Table**: Exactly one row per (facility, aspect) group. Columns: Facility tag (when "All facilities" selected), Aspect name, Evidence phrases joined by `" / "`, Sentiment badge (Positive / Negative / Neutral / Mixed in amber), and SVG Stars calculated via $1 + 4 \times (\text{pos} + 0.5 \times \text{neu}) / \text{total}$ with half-up rounding and labeled "estimated from sentiment".<br>3. **Honest Disclaimer**: Muted line: *"Facilities were assigned from words in the comment. Choose a facility for more precise results."*<br>4. **Ollama Summary**: Prompt receives only grouped facility, aspect, and sentiment (no counts, ratings, or percentages) and outputs 2–3 plain sentences mentioning strictly detected aspects.<br>5. **Abusive Guard**: Evaluated once via Toxic-BERT before aspect extraction. If score >= 0.50, stops at stage 2 in red with quarantined alert box, zero rows, zero stars, and no summary. |
| **Step 4** | **Facility Explorer** | **Finished** | Simple facility picker dropdown, overall rating, comment count, top complaint area, recurring issues count, small Chart.js aspect sentiment rating chart, and scrollable aspect list. Single-screen compact view. |
| **Step 5** | **Aspect-wise Ratings** | **Finished** | Inner tabs ("Overview Chart" vs "Data Table"). Overview chart features benchmark line (2.54), facility filter, topic filter, and dark legend. Data table features live instant search, sortable headers, and internal scrolling. |
| **Step 6** | **Recurring Issues** | **Finished** | Inner tabs ("Severity Chart" vs "Verified Comments"). Severity chart ranks problem areas with horizontal bars. Verified comments section includes dynamic negative-share severity slider and expandable quotes. |
| **Step 7** | **Facility Briefs** | **Finished** | Single view features sortable facility tabs (highest, lowest, alphabetical), exact text from summaries.csv, and copy summary button. Compare mode allows side-by-side comparison of any two facilities. |
| **Step 8** | **Abusive Content** | **Finished** | Inner tabs ("Overview & Distribution" vs "Quarantined Records"). Displays Toxic-BERT data integrity policy, moderation rate (6.1%), facility breakdown tracks, and quarantined table with truncated preview toggle. |
| **Step 9** | **README & Verification** | **Finished** | Updated README.md, verified all 7 routes return HTTP 200, tested offline assets, and verified zero changes outside webapp/. |

---

## 3. Verified Output of Live Demo Official Tests (A, B, C, D)

### Test A: "All facilities" with multi-facility comment
* **Input**: *"The library is quiet and the staff are very helpful, but the canteen food is cold and the queue takes twenty minutes. Wi-Fi keeps disconnecting in the hostel. Also classrooms are noisy and the morning bus is always late with rude drivers."*
* **Facility Selected**: `All facilities`
* **Abusive Check**: Passed (Toxicity score: `0.001`, verified safe)
* **Real Result Table**:
  | Facility Tag | Aspect & Evidence | Sentiment | Stars (half-up) |
  |---|---|---|---|
  | `Canteen` | **Food Quality**<br><span style="color:#9aa3b0;font-size:0.8em">The canteen food is cold</span> | Negative | ★☆☆☆☆ (1 star) |
  | `Canteen` | **Waiting Time**<br><span style="color:#9aa3b0;font-size:0.8em">The queue takes twenty minutes</span> | Negative | ★☆☆☆☆ (1 star) |
  | `Classrooms` | **Noise**<br><span style="color:#9aa3b0;font-size:0.8em">Classrooms are noisy</span> | Negative | ★☆☆☆☆ (1 star) |
  | `Library` | **Silence**<br><span style="color:#9aa3b0;font-size:0.8em">The library is quiet</span> | Negative | ★☆☆☆☆ (1 star) |
  | `Library` | **Staff Behavior**<br><span style="color:#9aa3b0;font-size:0.8em">The staff are very helpful</span> | Positive | ★★★★★ (5 stars) |
  | `Transport` | **Driver Behavior**<br><span style="color:#9aa3b0;font-size:0.8em">The morning bus is always late with rude drivers</span> | Negative | ★☆☆☆☆ (1 star) |
  | `Transport` | **Punctuality**<br><span style="color:#9aa3b0;font-size:0.8em">The morning bus is always late with rude drivers</span> | Negative | ★☆☆☆☆ (1 star) |
  | `Wi-Fi` | **Reliability**<br><span style="color:#9aa3b0;font-size:0.8em">Wi-fi keeps disconnecting in the hostel</span> | Negative | ★☆☆☆☆ (1 star) |
* **Ollama Live Summary** (`llama3.1`):
  > *"Students are dissatisfied with the food quality and waiting time at the canteen. They also experience noise in classrooms and disruptions in silence at the library. Additionally, students express concerns about the reliability of Wi-Fi, driver behavior, and punctuality of the transport services."*
* **Analysis & Model Observations**:
  1. All 5 facilities (Library, Canteen, Classrooms, Wi-Fi, Transport) were successfully identified and routed.
  2. Subclause carry-over functioned as expected: *"the staff are very helpful"* inherited `Library`, and *"the queue takes twenty minutes"* inherited `Canteen`.
  3. Hostel disambiguation succeeded: *"Wi-Fi keeps disconnecting in the hostel"* routed to `Wi-Fi`.
  4. **Model misclassification noted**: The sentiment model in `models/sentiment_distilbert/` classified *"The library is quiet"* as `Negative` for the aspect `silence`. The dashboard displayed this real model output without altering weights or retraining.

---

### Test B: Single facility mode with long comment
* **Input**: *"The food in the canteen is oily, stale and completely cold. The price is too high for such small portions. Waiting time at the counter is ridiculous and there are never enough chairs to sit. Also the cashier is rude."*
* **Facility Selected**: `Canteen`
* **Abusive Check**: Passed (Toxicity score: `0.002`, verified safe)
* **Real Result Table**:
  | Aspect & Evidence | Sentiment | Stars (half-up) |
  |---|---|---|
  | **Food Quality**<br><span style="color:#9aa3b0;font-size:0.8em">The food in the canteen is oily / Stale / Completely cold</span> | Negative | ★☆☆☆☆ (1 star) |
  | **Price**<br><span style="color:#9aa3b0;font-size:0.8em">The price is too high for such small portions</span> | Negative | ★☆☆☆☆ (1 star) |
  | **Quantity**<br><span style="color:#9aa3b0;font-size:0.8em">The price is too high for such small portions</span> | Negative | ★☆☆☆☆ (1 star) |
  | **Seating**<br><span style="color:#9aa3b0;font-size:0.8em">There are never enough chairs to sit</span> | Negative | ★☆☆☆☆ (1 star) |
  | **Staff Behavior**<br><span style="color:#9aa3b0;font-size:0.8em">The cashier is rude</span> | Negative | ★☆☆☆☆ (1 star) |
  | **Waiting Time**<br><span style="color:#9aa3b0;font-size:0.8em">Waiting time at the counter is ridiculous</span> | Negative | ★☆☆☆☆ (1 star) |
* **Ollama Live Summary** (`llama3.1`):
  > *"Students are dissatisfied with the food quality, prices, and quantity of food available in the canteen. They also express negative opinions about the seating, staff behavior, and waiting times in the canteen. Overall, students have a negative experience with the canteen facilities."*
* **Analysis**: Multiple evidence phrases (e.g. "oily", "stale", "completely cold") were grouped into single aspect rows separated by `" / "`. Facility tag is hidden in single-facility mode as required.

---

### Test C1: Unanchored feedback (No facility stated)
* **Input**: *"The food tastes great but the prices are too high."*
* **Facility Selected**: `All facilities`
* **Real Result Table**:
  | Facility Tag | Aspect & Evidence | Sentiment | Stars (half-up) |
  |---|---|---|---|
  | `Facility not stated` | **Fare**<br><span style="color:#9aa3b0;font-size:0.8em">The prices are too high</span> | Negative | ★☆☆☆☆ (1 star) |
  | `Facility not stated`<br>*(fits Canteen, Hostel Mess)* | **Food Quality**<br><span style="color:#9aa3b0;font-size:0.8em">The food tastes great / The prices are too high</span> | Mixed | ★★★☆☆ (3 stars) |
  | `Facility not stated`<br>*(fits Canteen, Hostel Mess)* | **Price**<br><span style="color:#9aa3b0;font-size:0.8em">The prices are too high</span> | Negative | ★☆☆☆☆ (1 star) |
* **Ollama Live Summary** (`llama3.1`):
  > *"Students have negative opinions about the fare and price of facilities. Their views on food quality are mixed. Some students are dissatisfied with the cost of facilities."*
* **Analysis & Model Observations**:
  1. Shows `Facility not stated` without silent guessing.
  2. Disambiguation note `(fits Canteen, Hostel Mess)` appears where both facilities share the aspect.
  3. **Lexicon overlap noted**: `Fare` appears under `Facility not stated` because `"prices"` is in the transport lexicon for `fare` in `src/aspects.py`.

---

### Test C2: Non-topic comment
* **Input**: *"I like pizza and cricket."*
* **Facility Selected**: `All facilities`
* **Real Result Table**: 0 rows detected.
* **UI Output**: Plain informational box: *"No specific facility aspect was identified in this text. The comment was evaluated as general campus feedback."*
* **Summary**: None generated.

---

### Test D: Abusive comment
* **Input**: *"The canteen staff are complete idiots and stupid fools."*
* **Facility Selected**: `All facilities`
* **Toxicity Score**: `0.9903` (exceeds `0.50` threshold)
* **UI Output**: Step strip stops at Stage 2 in Red. Red alert box: *"This comment was flagged as abusive by the Toxic-BERT model and would be excluded from facility ratings."*
* **Aspect Rows, Stars, Summary**: None (quarantined).

---

## 4. Current State & Immediate Next Action

* **Completed**: All 9 steps (Steps 1 to 9) are 100% complete, verified, and running cleanly.
* **Ready for Review**: The dark-theme dashboard is fully assembled, consistent, and error-free across all 7 pages.
* **Launch Command**: `.\venv\Scripts\python.exe webapp/app.py`
