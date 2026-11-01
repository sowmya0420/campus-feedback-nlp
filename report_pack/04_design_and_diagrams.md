# Chapter 4: Design Approach and Details

This document provides the complete material for **Chapter 4** of the project report, detailing the high-level system architecture and detailed software engineering diagrams (Data Flow Diagrams Level 0 & 1, Use Case Diagram, Class Diagram, and Sequence Diagram).

All diagram source files (`.mmd` for Mermaid, `.puml` for PlantUML) and high-resolution, print-ready images (`.png` in plum theme `#4a2c6d` with white backgrounds and clear typography) are located in the companion folder [`report_pack/04_diagrams/`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/).

---

## 4.1 System Architecture

The **Campus Facility Feedback Analysis System** is structured as an end-to-end, multi-layered data engineering and Natural Language Processing architecture. It decouples user interaction, deep learning inference, quantitative aggregation, and persistence layers into distinct, modular subsystems.

### Architecture Overview

The system architecture comprises four primary logical tiers:

1. **User Interaction & Presentation Tier**:
   - **Flask Offline Web Application (`webapp/app.py`)**: The primary production interface operating locally at `http://127.0.0.1:5000`. It features seven distinct offline views: Home KPI cards, Live Demo, Facility Explorer, Aspect-wise Ratings, Recurring Issues, Facility Briefs, and Abusive Moderation. It incorporates intelligent multi-facility clause routing, carrying context across conjunctions and disambiguating complex sentences (e.g., distinguishing Wi-Fi complaints from room complaints in hostel reviews).
   - **Streamlit Internal Prototyping Dashboard (`app/app.py`)**: A rapid internal dashboard used during initial development to visualize distributions using Plotly charts.

2. **Natural Language Processing (NLP) Pipeline Tier (`src/pipeline.py`)**:
   - **Text Normalization & Clause Segmentation (`src/preprocess.py`)**: Cleans informal student talk, normalizes stretched vowels, resolves colloquial Tanglish slang terms, and segments compound sentences into clauses using punctuation boundaries and contrast conjunctions (`but`, `however`, `aanaal`).
   - **Abusive Content Quarantine Gate (`unitary/toxic-bert`)**: A pre-filtering classifier evaluated once per comment. Any comment scoring equal to or above the threshold ($\tau = 0.50$) is tagged as abusive and routed directly to a quarantined database, preventing toxic remarks from distorting facility ratings.
   - **Hybrid Aspect Extractor (`src/aspects_hybrid.py`)**: Employs a dual-engine approach. A high-speed regular expression keyword matcher (`src/aspects.py`) extracts known domain terms and categories. When keywords miss subtle expressions, a multi-label DistilBERT topic model (`models/aspect_distilbert_v1`) appends candidate categories when prediction confidence is at least 50% (`ADD_CONF = 0.50`).
   - **Aspect-Based Sentiment Classifier (`models/sentiment_distilbert_v3`)**: A fine-tuned sequence classification transformer that accepts the combined input `[aspect term]` + `[subclause]` and outputs the predicted polarity: `positive`, `neutral`, or `negative`.

3. **Analytics, Metric Aggregation & Summarization Tier**:
   - **Quantitative Aggregation Engine (`src/aggregate.py`)**: Mathematically aggregates individual aspect predictions into standard 1.0 to 5.0 star ratings for each facility and each aspect. Automatically detects chronic recurring issues by applying a strict 70% negative mention threshold (`ISSUE_NEG_SHARE = 0.70`).
   - **Factual Executive Summarizer (`src/summarize.py` & `src/summarize_ai.py`)**: Integrates with a local LLaMA 3.1 model running via the Ollama daemon. Formulates structured factual prompts and passes the generated text through an automated verification gate (`looks_wrong`) to reject any fabricated numbers, falling back to a deterministic template if necessary.

4. **Data Artifact Storage Tier (`data/outputs/`)**:
   - An immutable, file-based persistence store holding `predictions.csv` (1,056 aspect records), `ratings.csv` (8 facility ratings and 42 aspect ratings), `issues.csv` (16 chronic problem alerts), and `summaries.csv` (8 factual facility briefs).

```
+---------------------------------------------------------------------------------------------------+
|                                  USER INTERACTION LAYER                                           |
|       Student User (Live Demo Form)        |      College Administrator (Analytics Dashboard)     |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                     NLP PIPELINE TIER                                             |
|  [1. Preprocessing] -> [2. Toxic-BERT Gate] -> [3. Hybrid Aspect Finder] -> [4. DistilBERT ABSA] |
|   (Clause Splitting)     (Cutoff >= 0.50)       (Keywords + DistilBERT)        (Pos / Neu / Neg)  |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                METRIC AGGREGATION & SUMMARY TIER                                  |
|         [5. Aggregation Engine]                |             [6. Local Ollama LLM]                |
|    (1-5 Star Ratings, Neg Share >= 70%)        |        (Fact-Checked LLaMA 3.1 Summaries)        |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                     STORAGE ARTIFACT TIER                                         |
|      predictions.csv       |      ratings.csv      |      issues.csv      |     summaries.csv     |
+---------------------------------------------------------------------------------------------------+
```

---

### Figure 4.1: System Architecture Diagram

![System Architecture](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/01_system_architecture.png)

*Figure 4.1: End-to-end multi-tiered system architecture showing data movement from student submission through preprocessing, toxicity screening, aspect extraction, sentiment analysis, metric aggregation, and offline dashboard presentation.*

- **Diagram Files**:
  - Image: [`01_system_architecture.png`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/01_system_architecture.png)
  - Mermaid Source: [`01_system_architecture.mmd`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/01_system_architecture.mmd)
  - PlantUML Source: [`01_system_architecture.puml`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/01_system_architecture.puml)

---

## 4.2 Detailed Design

### 4.2.1 Data Flow Diagrams (DFD)

Data Flow Diagrams map the path data takes through the system, identifying external entities, processing functions, and data stores.

#### 1. DFD Level 0 (Context Level Diagram)
The Level 0 Context Diagram depicts the entire system as a single central process interacting with external entities (Students and College Administrators).

![DFD Level 0](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/02_dfd_level_0.png)

*Figure 4.2: Data Flow Diagram Level 0 (Context Level) illustrating boundary data exchanges between Student Users, the central Feedback Analysis System, and College Administration.*

- **Diagram Files**:
  - Image: [`02_dfd_level_0.png`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/02_dfd_level_0.png)
  - Mermaid Source: [`02_dfd_level_0.mmd`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/02_dfd_level_0.mmd)
  - PlantUML Source: [`02_dfd_level_0.puml`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/02_dfd_level_0.puml)

#### 2. DFD Level 1 (Detailed Subsystem Decomposition)
The Level 1 diagram decomposes the system into six distinct functional processes (1.0 Preprocessing, 2.0 Abuse Screening, 3.0 Aspect Extraction, 4.0 Sentiment Classification, 5.0 Metrics Aggregation, and 6.0 Summary Generation) and five underlying data stores (D1 Quarantined Abuse, D2 Predictions Store, D3 Ratings Store, D4 Issues Store, and D5 Summaries Store).

![DFD Level 1](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/03_dfd_level_1.png)

*Figure 4.3: Data Flow Diagram Level 1 decomposing internal pipeline processes, intermediate data transformations, and specific persistence stores from raw input to executive outputs.*

- **Diagram Files**:
  - Image: [`03_dfd_level_1.png`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/03_dfd_level_1.png)
  - Mermaid Source: [`03_dfd_level_1.mmd`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/03_dfd_level_1.mmd)
  - PlantUML Source: [`03_dfd_level_1.puml`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/03_dfd_level_1.puml)

---

### 4.2.2 Use Case Diagram

The Use Case diagram specifies system functionality from the perspective of two primary actors:
1. **Student User**: Day scholars, hostellers, and outstation students who submit anonymous qualitative feedback and inspect instant sentiment ratings.
2. **College Facility Administrator**: Department heads, hostel wardens, canteen committee members, and estate managers who monitor operational facility health, track recurring grievances, and review executive briefs.

![Use Case Diagram](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/04_use_case_diagram.png)

*Figure 4.4: Use Case Diagram mapping student interactions and administrative analytical capabilities across the eight primary system functions.*

- **Diagram Files**:
  - Image: [`04_use_case_diagram.png`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/04_use_case_diagram.png)
  - Mermaid Source: [`04_use_case_diagram.mmd`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/04_use_case_diagram.mmd)
  - PlantUML Source: [`04_use_case_diagram.puml`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/04_use_case_diagram.puml)

---

### 4.2.3 Class Diagram (Real Classes & Architectural Modules)

The Class Diagram reflects the actual object-oriented and functional modular structure implemented across `src/` and `webapp/`:
- **`DS` (Dataset Wrapper Class in Notebooks)**: PyTorch `torch.utils.data.Dataset` subclass managing tokenization dictionaries and label tensor alignment.
- **`Pipeline` Module (`src/pipeline.py`)**: Coordinates end-to-end execution, holding the Hugging Face text-classification pipeline instance for `unitary/toxic-bert`.
- **`AspectsHybrid` Module (`src/aspects_hybrid.py`)**: Glues the deterministic `AspectsKeyword` regex engine with the deep-learning `AspectsDistilBERT` probability scorer.
- **`SentimentEngine` Module (`src/sentiment.py`)**: Encapsulates the DistilBERT sequence classifier and VADER lexicon backup.
- **`Aggregator` Module (`src/aggregate.py`)**: Implements mathematical star rating logic and recurring issue thresholds.
- **`Summarizer` Module (`src/summarize.py`)**: Manages Ollama HTTP requests and regex validation.
- **`FlaskWebApp` Controller (`webapp/app.py`)**: Handles HTTP routing, clause routing logic, and template context injection.

![Class Diagram](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/05_class_diagram.png)

*Figure 4.5: Class and Module Diagram illustrating the real software components, primary member methods, attributes, and inter-module dependencies implemented in the codebase.*

- **Diagram Files**:
  - Image: [`05_class_diagram.png`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/05_class_diagram.png)
  - Mermaid Source: [`05_class_diagram.mmd`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/05_class_diagram.mmd)
  - PlantUML Source: [`05_class_diagram.puml`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/05_class_diagram.puml)

---

### 4.2.4 Sequence Diagram

The Sequence Diagram captures the dynamic, step-by-step lifecycle of a student submitting feedback on the web interface, illustrating the quarantine branch for abusive text and the multi-stage analysis loop for safe feedback.

![Sequence Diagram](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/06_sequence_diagram.png)

*Figure 4.6: Sequence Diagram showing chronological message exchanges and conditional branching during real-time student feedback submission and analysis.*

- **Diagram Files**:
  - Image: [`06_sequence_diagram.png`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/06_sequence_diagram.png)
  - Mermaid Source: [`06_sequence_diagram.mmd`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/06_sequence_diagram.mmd)
  - PlantUML Source: [`06_sequence_diagram.puml`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/06_sequence_diagram.puml)
