# Chapter 5: Methodology and Testing

This document provides the complete material for **Chapter 5** of the project report, detailing the seven engineering modules, dataset provenance and split audits, the rationale for neutral data supplementation, model training specifications, evaluation metrics, and comprehensive testing methodologies.

---

## 5.1 Module Descriptions (The 7 Pipeline Modules)

The pipeline is organized into seven sequential functional modules. To demonstrate engineering rigor, each module documents both its baseline prototype and its upgraded deep-learning implementation.

---

### Module 1: Text Preprocessing and Clause Segmentation
- **What it does**: Cleans informal student writing, normalizes colloquial Tanglish slang, standardizes character repetition, and splits compound sentences into independent semantic clauses.
- **The Method**: Employs regular expressions (`re`) and deterministic string transformations:
  1. *Normalization*: Strips typographic apostrophes, standardizes whitespace, lowercases all text, and shortens stretched characters (e.g., regex `r"(.)\1{2,}"` converts `"sooooo"` to `"soo"`).
  2. *Clause Splitting*: Segments text on punctuation boundaries (`PUNCT = r"[;,!?]+|(?<!\d)\.|\.(?!\d)"` to avoid breaking decimals like `"2.5"`) and semantic contrast markers (`CONTRAST = r"\b(?:but|however|though|although|yet|aana|aanaal|anaal)\b"`).
  3. *Clause Targeting*: Matches each aspect term to its specific surrounding clause (`clause_with_term`), ensuring that sentiments are evaluated in local context rather than across the whole paragraph.
- **Why this method**: Real student comments regularly combine multiple opposing thoughts in one breath (e.g., *"Food is tasty but the price is too high"*). Without clause segmentation, positive adjectives in one clause bleed into complaints in another.
- **Input**: Raw comment string (e.g., `"Food is good but queue romba long"`).
- **Output**: List of cleaned, segmented clause strings.
- **Source File**: [`src/preprocess.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/preprocess.py)

---

### Module 2: Aspect Extraction and Category Detection
- **What it does**: Identifies which specific campus features or topics are mentioned in the comment and maps them to standard category labels.
- **Baseline Version**:
  - *Method*: Keyword-based pattern matching (`src/aspects.py`). Uses a hardcoded domain lexicon across 8 facilities, matching terms with compiled regular expressions allowing optional plural suffixes `(?:s|es)?`.
  - *Shortcoming*: Fails completely when students express complaints using vocabulary outside the dictionary (e.g., missed 33% of aspects on validation, F1: 0.698).
- **Upgraded Version (Hybrid System - Final)**:
  - *Method*: Hybrid architecture (`src/aspects_hybrid.py`). First runs the fast regex keyword matcher. Simultaneously, passes the comment through a multi-label DistilBERT topic model (`models/aspect_distilbert_v1`). If the topic model predicts a valid facility aspect with confidence $\ge 0.50$ (`ADD_CONF = 0.50`) that the keywords missed, the model adds that aspect to the record.
  - *Why this method*: Combines the precision and exact term-extraction of regex with the broad contextual understanding of a transformer neural network.
- **Input**: Comment text and facility identifier (e.g., `"The bus arrived twenty minutes late"`, `"transport"`).
- **Output**: List of aspect dictionaries: `[{"aspect_term": "late", "category": "punctuality", "clause": "The bus arrived twenty minutes late"}]`.
- **Source Files**: [`src/aspects.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/aspects.py), [`src/aspects_bert.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/aspects_bert.py), [`src/aspects_hybrid.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/aspects_hybrid.py)

---

### Module 3: Aspect-Based Sentiment Analysis (ABSA)
- **What it does**: Classifies the emotional attitude of the student toward each detected aspect into one of three classes: `positive`, `neutral`, or `negative`.
- **Baseline Version**:
  - *Method*: VADER (Valence Aware Dictionary for sEntiment Reasoning) supplemented with a custom campus and Tanglish word list (`CAMPUS_WORDS` and `OVERRIDES` in `src/sentiment.py`).
  - *Shortcoming*: Rule-based valences cannot handle subtle sentence context, complex negations, or domain transfer, achieving only 0.687 macro-F1 on validation.
- **Upgraded Version (DistilBERT v3 - Final)**:
  - *Method*: Sequence classification transformer fine-tuned on aspect-clause pairs. The input to the tokenizer is formatted as:
    $$\text{Tokenizer Input: } \text{[aspect term or category]} \ + \ \text{[clause text]}$$
    The model feeds the tokenized representations through 6 transformer layers and a sequence classification head, outputting softmax probabilities over 3 classes.
  - *Why this method*: DistilBERT learns complex contextual relationships and subtle semantic dependencies between the aspect term and surrounding modifying words, vastly outperforming dictionary lookups.
- **Input**: Segmented clause string and aspect term/category string.
- **Output**: Sentiment label string (`"positive"`, `"neutral"`, or `"negative"`).
- **Source Files**: [`src/sentiment.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/sentiment.py), [`src/sentiment_bert.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/sentiment_bert.py), [`models/sentiment_distilbert_v3/`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/models/sentiment_distilbert_v3)

---

### Module 4: Quantitative Facility Ratings Aggregation
- **What it does**: Transforms discrete sentiment classifications into standardized numerical grades (1.0 to 5.0 stars) for each facility and each aspect.
- **The Method**: Filters out all abusive comments (`abusive == True`) and unanchored general comments (`category == "general"`). For every remaining facility and aspect group $g$, computes the rating using the normalized formula:
  $$\text{Rating}(g) = 1.0 + 4.0 \times \left( \frac{N_{\text{pos}} + 0.5 \times N_{\text{neu}}}{N_{\text{total}}} \right)$$
  Where $N_{\text{pos}}$ is the count of positive mentions, $N_{\text{neu}}$ is the count of neutral mentions, and $N_{\text{total}}$ is the total mentions for that category. The overall facility rating aggregates all aspect mentions across that facility.
- **Why this method**: Produces an intuitive, human-understandable 1 to 5 star rating scale familiar to academic administrators and students, giving positive feedback full weight (1.0), neutral feedback half weight (0.5), and negative feedback zero weight.
- **Input**: `data/outputs/predictions.csv` (1,056 aspect prediction rows).
- **Output**: `data/outputs/ratings.csv` (8 facility overall rows and 42 individual aspect rows).
- **Source File**: [`src/aggregate.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/aggregate.py)

---

### Module 5: Recurring Chronic Issues Identification
- **What it does**: Scans the aggregated metrics to automatically isolate and rank severe operational problems requiring immediate administrative intervention.
- **The Method**: Evaluates each aspect against two statistical criteria:
  1. *Severity Criterion*: Negative mention ratio must equal or exceed 70% (`negative_share >= 0.70` where $\text{negative\_share} = N_{\text{neg}} / N_{\text{total}}$).
  2. *Significance Criterion*: Aspect must have at least 5 total mentions (`mentions >= 5`) to prevent isolated one-off complaints from triggering false alarms.
- **Why this method**: Prevents administrators from being distracted by minor complaints and highlights systemic, chronic failures (e.g., dining hall waiting times, hostel room water supply cuts, or bus overcrowding).
- **Input**: Aggregated aspect records from `src/aggregate.py`.
- **Output**: `data/outputs/issues.csv` (16 ranked recurring issues across 7 facilities).
- **Source File**: [`src/aggregate.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/aggregate.py)

---

### Module 6: Executive Facility Summarization
- **What it does**: Synthesizes tabular facility ratings and complaint statistics into a concise, 2-to-3 sentence executive natural language brief.
- **Baseline Version**:
  - *Method*: Deterministic string concatenation template (`summary()` in `src/summarize.py`). Formats top negative and positive aspects into fixed sentence templates.
  - *Shortcoming*: Output feels robotic, repetitive, and lacks linguistic variation across facilities.
- **Upgraded Version (Local LLaMA 3.1 + Verification Gate - Final)**:
  - *Method*: Queries a locally hosted Large Language Model (`llama3.1` via Ollama) using a strictly structured factual prompt (`facts_text()`).
  - *Automated Verification Gate (`looks_wrong()`)*: Before accepting the AI-generated text, an automated regex validator scans the summary:
    - Verifies that every percentage cited (regex `r"\d+%"`) appears verbatim in the input facts.
    - Ensures that phrases like *"few complaints"* are only present if an area actually had $<40\%$ negative feedback.
    - Confirms that every aspect category mentioned exists in the input facts.
    If the AI fails any check, the system retries up to 3 times; if it still fails, it automatically falls back to the deterministic template.
- **Input**: Aggregated numerical facts for a facility.
- **Output**: `data/outputs/summaries.csv` (8 factual facility briefs).
- **Source Files**: [`src/summarize.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/summarize.py), [`src/summarize_ai.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/summarize_ai.py)

---

### Module 7: Abusive and Toxic Content Detection
- **What it does**: Screens incoming student comments for toxic language, profanity, and personal insults, quarantining them to protect data integrity.
- **Baseline Version**:
  - *Method*: Scikit-Learn pipeline combining TF-IDF word and bi-gram vectorization (`ngram_range=(1,2)`, `max_features=200,000`) with Logistic Regression (`class_weight="balanced"`, $C=4.0$), trained on the Jigsaw Toxic Comment dataset (`src/toxicity_baseline.py`).
  - *Shortcoming*: Missed subtle insults and generated **25 false alarms** on normal campus complaints (precision only 63.2%).
- **Upgraded Version (`unitary/toxic-bert` - Final)**:
  - *Method*: Employs the pre-trained `unitary/toxic-bert` transformer model (`src/toxicity_bert.py`). The comment text is tokenized (maximum length 128) and passed through the model. The maximum score across all six toxicity heads is compared against a threshold of $\tau = 0.50$.
  - *Why this method*: Deep self-attention representations distinguish between legitimate harsh complaints (e.g., *"the bathroom is disgusting"*) and true toxic personal abuse, reducing false alarms from 25 down to **6** and boosting precision from 63% to **88%**.
- **Input**: Raw comment string.
- **Output**: Boolean flag (`abusive: true/false`), toxicity score, and quarantined database entry.
- **Source Files**: [`src/toxicity_baseline.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/toxicity_baseline.py), [`src/toxicity_bert.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/toxicity_bert.py), [`src/compare_toxicity.py`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/src/compare_toxicity.py)

---

## 5.2 Datasets and Provenance Accounting

### 5.2.1 Primary Campus Facility Feedback Dataset
The primary dataset consists of synthetic student feedback engineered specifically to simulate the linguistic diversity of higher education campuses in Tamil Nadu, India.
- **Generation Method**: Synthesized using structured prompt batches (`PROMPT.md`) requiring specific persona distributions (first-year hostellers, day scholars, final-year students, outstation students, club members, and backlog students).
- **Volume & Accounting**: Exactly 800 total comments generated across 16 discrete batches (2 batches per facility, 50 comments per batch, 100 comments per facility).
- **Abusive Distribution**: Exactly 3 comments per batch were generated as toxic/abusive, producing exactly 48 ground-truth abusive comments (6.0% global toxicity rate).
- **Language Composition**: Approximately 15% to 40% of comments feature bilingual Tanglish code-mixing (English interspersed with Romanized Tamil terms).

#### Partitioning and Zero-Leakage Audit:
The dataset was partitioned at the comment level using a fixed random seed (`SEED = 42`):
- **Training Set (70%)**: 560 comments, 649 original aspects, 32 abusive comments.
- **Validation Set (15%)**: 120 comments, 134 original aspects, 8 abusive comments.
- **Test Set (15%)**: 120 comments, 132 original aspects, 8 abusive comments.
- **Leakage Audit**: Verified using automated tests (`src/validate_dataset.py`). Zero comment ID overlap, zero exact text overlap, and zero near-duplicate pairs (Jaccard similarity $< 0.85$) across splits.

---

### 5.2.2 Why Neutral Comments Were Added Later (Neutral Data Supplementation)

During Phase 2 and Phase 3 of development, an empirical inspection revealed a critical dataset weakness:

1. **Initial Severe Class Imbalance**:
   In the original 800 synthetic comments, aspect sentiment was heavily skewed toward polarity extremes:
   - Negative aspects: **529** (57.8%)
   - Positive aspects: **362** (39.6%)
   - Neutral aspects: only **24** out of 915 aspects (**2.6%**)!
   In the original validation split, there were only 3 neutral aspects; in the test split, there were only 3 neutral aspects.

2. **The "Zero Neutral" Failure in DistilBERT v2**:
   When DistilBERT v2 was fine-tuned on the original training set and evaluated on the campus validation set in Google Colab (`colab_sentiment_distilbert.ipynb`, Cell 26), the confusion matrix revealed a complete failure on the neutral class:
   ```
   Confusion Matrix:
   [[50   0  10]    rows = true labels ['positive', 'neutral', 'negative']
    [ 9   0   9]    The model predicted ZERO neutral labels!
    [ 0   0  71]]
   
   Class Metrics:
                 precision    recall  f1-score   support
       positive       0.85      0.83      0.84        60
        neutral       0.00      0.00      0.00        18
       negative       0.79      1.00      0.88        71
   ```
   Because the neural network had seen virtually zero neutral examples during training, it learned to ignore the neutral class entirely, scoring **0.00 F1-score for neutral** and dragging macro-F1 down to 0.574!

3. **The Supplementation Solution (`neutral_additions.csv`)**:
   To resolve this flaw without corrupting the original 800 comments, the team authored a targeted supplement file: `data/processed/neutral_additions.csv`.
   - **Total Neutral Additions**: Exactly **100** realistic, factual neutral aspect comments (e.g., *"mess queue takes around ten minutes, usual"*, *"water supply normal dhan, timing la varum"*, *"ac in the library is set at a normal level"*).
   - **Partitioning**: Split strictly according to the 70 / 15 / 15 ratio:
     - **70 neutral aspects** added to the **Training partition** (increasing train aspects from 649 to **719**).
     - **15 neutral aspects** added to the **Validation partition** (increasing validation aspects from 134 to **149**).
     - **15 neutral aspects** added to the **Test partition** (increasing test aspects from 132 to **147**).
   - **The Result**: Training DistilBERT v3 on the supplemented dataset allowed the model to master neutral expressions. On the validation set, neutral precision reached 0.72 and recall reached 0.72 (`colab_sentiment_distilbert.ipynb`, Cell 22), resolving the blind spot.

---

### 5.2.3 External Benchmark Datasets
- **EduRABSA Benchmark (Hua et al., 2025, arXiv:2508.17008)**: 4,000 training reviews (16,500 aspects) used strictly for educational domain pre-training of the sentiment model.
- **Jigsaw Toxic Comment Dataset (Kaggle)**: 159,571 comments used to train the TF-IDF + Logistic Regression baseline and provide a 2,000-comment out-of-domain benchmark for Toxic-BERT.

---

## 5.3 Models and Training Specifications

All deep learning training runs were conducted on Google Colaboratory using PyTorch and Hugging Face Transformers.

| Model Checkpoint | Task | Base Architecture | Training Dataset & Size | Hyperparameters & Environment |
|---|---|---|---|---|
| `models/sentiment_distilbert_v1` | Domain Pretraining | `distilbert-base-uncased` (66M params) | EduRABSA Train (16,500 rows) | 2 epochs, batch size 32, lr 2e-5, weight decay 0.01, FP16 enabled, Tesla T4 GPU |
| `models/sentiment_distilbert_v2` | Campus Fine-Tuning | `distilbert-base-uncased` | Original Campus Train (649 rows) | 3 epochs, batch size 16, lr 1e-5, weight decay 0.01, FP16 enabled, Tesla T4 GPU |
| `models/sentiment_distilbert_v3` (Final) | Balanced Fine-Tuning | `distilbert-base-uncased` | Supplemented Campus Train (719 rows) | 3 epochs, batch size 16, lr 1e-5, weight decay 0.01, FP16 enabled, Tesla T4 GPU |
| `models/aspect_distilbert_v1` | Multi-Label Topic Detection | `distilbert-base-uncased` | Campus Train (560 comments, multi-label) | 20 epochs, batch size 16, lr 5e-5, weight decay 0.01, problem type `multi_label_classification` |
| `models/toxicity_tfidf_logreg.joblib` | Baseline Abuse Classifier | TF-IDF (200k n-grams) + Logistic Regression | Jigsaw Train (154,571 comments) | max_iter 1000, class_weight="balanced", C=4.0, trained locally on CPU |
| `unitary/toxic-bert` (Final) | Production Abuse Classifier | `bert-base-uncased` fine-tuned on toxic text | Pre-trained by Unitary AI on Jigsaw | Zero-shot inference, threshold $\tau = 0.50$, evaluated locally |
| `llama3.1` via Ollama | Executive Summarizer | Meta LLaMA 3.1 8B Instruct (4-bit quantized) | Instruction-tuned foundation model | Local execution, temperature 0.2, constrained by regex fact-checker |

---

## 5.4 Evaluation Metrics Explained in Plain English

To ensure clarity for readers without machine learning backgrounds, the evaluation metrics used throughout this report are defined below:

1. **Accuracy**:
   - *Plain English*: The overall percentage of times the model guessed the right answer out of all test cases.
   - *Formula*:
     $$\text{Accuracy} = \frac{\text{Correct Predictions}}{\text{Total Predictions}} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$$

2. **Precision**:
   - *Plain English*: When the model flags something (e.g., claiming a comment is abusive), how often is it actually correct? High precision means very few false alarms.
   - *Formula*:
     $$\text{Precision} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$$

3. **Recall**:
   - *Plain English*: Out of all the real examples that actually existed (e.g., all 48 abusive comments), what percentage did the model successfully find? High recall means very few missed cases.
   - *Formula*:
     $$\text{Recall} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$$

4. **F1-Score**:
   - *Plain English*: The balanced harmonic average of precision and recall. It ensures a model cannot look good simply by guessing the majority class.
   - *Formula*:
     $$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

5. **Macro-F1 Score**:
   - *Plain English*: Computes the F1-score for each class independently (Positive F1, Neutral F1, and Negative F1) and then calculates their simple unweighted average. This ensures that rare classes (like Neutral) are treated with equal importance as frequent classes (like Negative).

---

## 5.5 Testing Strategy and Edge Case Validation

### 5.5.1 Validation vs Single Final Test Run
To maintain strict academic integrity and avoid data snooping:
- All hyperparameter tuning, keyword lexicon expansions, threshold selections ($\tau = 0.50$ for toxicity, $\text{ADD\_CONF} = 0.50$ for aspect additions, and $\text{ISSUE\_NEG\_SHARE} = 0.70$ for recurring issues) were conducted **strictly on the Validation partition**.
- The **Test partition (120 comments, 147 aspects)** was evaluated exactly **once, at the very end**, using the command:
  ```powershell
  python -m src.evaluate test --final
  ```
  This guarantees that test metrics reflect true out-of-sample generalization.

---

### 5.5.2 Edge Case Testing Across Five Linguistic Challenges

The system was evaluated against five challenging linguistic test scenarios:

1. **Complex Negation Handling**:
   - *Input*: *"The food is not bad at all and the price is not unreasonable."*
   - *Challenge*: Simple keyword models see `"bad"` and `"unreasonable"` and predict Negative.
   - *Result*: DistilBERT v3 successfully understands the double negations, predicting `Positive` for both food quality and price.

2. **Plain Fact Sentences (Neutrality Challenge)**:
   - *Input*: *"The library closes at 8 PM on weekdays."*
   - *Challenge*: Fact statements lack emotional adjectives. Earlier models defaulted to Negative.
   - *Result*: DistilBERT v3 correctly predicts `Neutral`.

3. **Mixed-Sentiment Compound Sentences**:
   - *Input*: *"The library is quiet and staff are helpful, but canteen food is cold and the queue takes twenty minutes."*
   - *Challenge*: Requires multi-facility clause routing and opposing sentiment extraction.
   - *Result*: Successfully routed to Library and Canteen. Library aspects scored Positive (5 stars); Canteen aspects scored Negative (1 star).

4. **Bilingual Tanglish Expressions**:
   - *Input*: *"Mess food romba waste, but tea semma super."*
   - *Challenge*: Romanized Tamil vocabulary (`"romba waste"` = very bad; `"semma super"` = excellent).
   - *Result*: Preprocessing and lexicon correctly mapped `"food"` to Negative (1 star) and `"tea"` to Positive (5 stars).

5. **Sarcasm and Indirect Criticism**:
   - *Input*: *"Great job keeping the fans off in 40 degree heat, wonderful experience."*
   - *Challenge*: Surface words are positive (`"great"`, `"wonderful"`), but the true intent is deeply critical.
   - *Known Limit*: In the live demo, this was classified as Positive because the model lacks broad multi-sentence irony detection. Documented honestly as a system limitation.
