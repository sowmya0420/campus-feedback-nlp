# Chapter 2: Project Description and Goals

This document provides the complete material for **Chapter 2** of the project report, covering the Literature Review foundations, Research Gap, Objectives, Problem Statement, and Chronological Project Plan.

---

## 2.1 Literature Review Topics & Foundation

To write Section 2.1 of the report, you should review academic literature in four major Natural Language Processing areas. Below are the key topics, their simple one-line definitions, and the exact real-world models, datasets, and libraries used in this project. 

> [!IMPORTANT]
> **Strict Fact-Checking Rule**: Do not invent paper titles or citations. Search for peer-reviewed papers matching the official names provided below, and verify the author list and publication details before adding them to your final bibliography. Every item below is marked with **VERIFY BEFORE CITING**.

### 1. Aspect-Based Sentiment Analysis (ABSA)
- **Concept in Plain English**: Unlike standard sentiment analysis which assigns one overall label to an entire text, ABSA identifies the specific entity or feature being discussed (the *aspect*) and determines the user's emotional attitude toward that specific feature.
- **Key Sub-tasks to Read About**:
  - *Aspect Term Extraction (ATE)*: Finding the exact words in the sentence that represent a feature (e.g., extracting `"sambar"` or `"wifi speed"`).
  - *Aspect Category Detection (ACD)*: Mapping extracted terms to higher-level domain buckets (e.g., mapping `"sambar"` to the category `"food quality"`).
  - *Aspect-Level Sentiment Classification (ALSC)*: Determining if the sentiment toward that category is positive, negative, or neutral.
- **Official Dataset Used in This Project**:
  - **EduRABSA Dataset** (`VERIFY BEFORE CITING`): An academic benchmark dataset created for aspect-based sentiment analysis in higher education evaluations. Introduced by Hua et al. (2025), *EduRABSA: A Benchmark Dataset for Aspect-Based Sentiment Analysis in Educational Reviews* (arXiv preprint: `arXiv:2508.17008`). It contains 4,000 training reviews (16,500 aspect annotations) and 2,500 test reviews (10,537 aspect annotations). In this project, EduRABSA was used for initial domain pre-training of the sentiment model.
  - **Synthetic Campus Facility Dataset** (`VERIFY BEFORE CITING`): Created specifically for this project following a structured prompt schema (`PROMPT.md`). Comprises 800 student comments (100 per facility across 8 facilities, 48 abusive comments, 915 original aspect annotations, plus 100 neutral supplement rows).

### 2. Transformer Architectures and DistilBERT
- **Concept in Plain English**: A transformer is a deep-learning model that uses a mechanism called *self-attention* to read entire sentences simultaneously, capturing subtle contextual relationships between words regardless of their distance in the text.
- **Why DistilBERT was Chosen**:
  - Full-scale models like BERT (Bidirectional Encoder Representations from Transformers) contain approximately 110 million parameters and require substantial memory and processing power.
  - **DistilBERT** (`VERIFY BEFORE CITING`): Developed by Sanh et al. (2019) at Hugging Face (*DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter*, arXiv:1910.01108). DistilBERT uses knowledge distillation during pre-training to compress BERT by 40% (retaining 66 million parameters) while preserving over 97% of BERT's language understanding capabilities and running 60% faster.
  - In this project, `distilbert-base-uncased` serves as the foundational pre-trained backbone for both aspect category extraction and fine-grained sentiment classification.

### 3. Toxic and Abusive Language Detection
- **Concept in Plain English**: Automated classification of text to identify whether a comment contains profanity, insults, identity attacks, or malicious harassment.
- **Official Dataset and Model Used in This Project**:
  - **Jigsaw Toxic Comment Classification Challenge** (`VERIFY BEFORE CITING`): A benchmark dataset released by Google and Jigsaw on Kaggle (2017–2018), containing 159,571 Wikipedia talk page comments labeled for toxicity, severe toxicity, insults, and identity attacks. In this project, a balanced 5,000-row sample was used to evaluate baseline models.
  - **`unitary/toxic-bert` Model** (`VERIFY BEFORE CITING`): A specialized transformer model developed by Unitary AI, fine-tuned on the Jigsaw toxic comment datasets to output probabilities across six toxicity dimensions. In this project, it operates as an automated moderation gate using a cutoff threshold of $\tau = 0.50$.

### 4. Text Summarization and Local Large Language Models (LLMs)
- **Concept in Plain English**: Using natural language generation models to compress quantitative tables and lengthy text into short, human-readable executive summaries without altering facts.
- **Local AI Framework Used in This Project**:
  - **LLaMA 3.1 (8B Parameters)** (`VERIFY BEFORE CITING`): An open-weights large language model released by Meta AI (2024), capable of high-fidelity instruction-following and zero-shot reasoning.
  - **Ollama Local Runtime** (`VERIFY BEFORE CITING`): An open-source local inference engine that serves quantized LLMs directly on consumer hardware (such as laptops) via a local REST API without transmitting confidential student feedback to external paid cloud APIs.
  - **Hallucination Prevention**: In NLP, *hallucination* refers to a language model generating confident statements containing false numbers or topics not present in the source prompt. In this project, an automated regex verification function (`src/summarize.py`) inspects LLM outputs to guarantee that all generated percentages and topics exist strictly in the factual input data.

---

## 2.2 Research Gap

A critical survey of current academic literature and commercial campus software reveals three distinct research and implementation gaps:

1. **Lack of Fine-Grained Infrastructure Feedback Systems**:
   Existing educational NLP research predominantly focuses on analyzing student evaluations of teaching (SET) or online course feedback (e.g., Coursera or RateMyProfessors reviews). Very few studies investigate student opinions regarding campus physical infrastructure (such as dorm hygiene, lab apparatus condition, transport punctuality, and dining hall nutrition), despite infrastructure having an enormous impact on daily student well-being.

2. **Inability to Handle Informal Indian English and Tanglish Code-Mixing**:
   Standard commercial sentiment engines (such as AWS Comprehend or Google Cloud Natural Language API) and academic lexicon tools (such as standard VADER or TextBlob) assume standard English grammar and vocabulary. They fail when processing Indian campus slang, spelling simplifications, and bilingual Tamil-English code-mixed phrases (Tanglish). When students write *"wifi speed average dhan"* or *"food semma but queue romba long"*, standard sentiment tools either fail completely or classify neutral/positive phrases as negative.

3. **Absence of End-to-End Governance and Integrity Controls**:
   Most published NLP studies treat aspect extraction, sentiment analysis, and toxicity detection as isolated academic benchmarks evaluated on separate, disconnected datasets. In a real-world institutional setting, an administrator requires a unified system where abusive comments are quarantined *before* ratings are calculated, multi-aspect sentences are routed automatically to appropriate department heads, and quantitative ratings are summarized into factual executive text without artificial intelligence hallucinations.

---

## 2.3 Objectives

The primary aim of this project is to design, implement, evaluate, and deploy an end-to-end NLP-based campus facility feedback analysis system. The specific technical objectives are:

1. **Dataset Synthesis and Quality Reconciliation**:
   To synthesize and validate a standardized dataset of 800 campus facility comments across eight facilities, incorporating localized Tanglish vocabulary, 42 aspect categories, 3-class sentiment labels, and a balanced subset of neutral and abusive comments with zero data leakage across train, validation, and test splits.

2. **Automated Abuse Screening and Rating Protection**:
   To implement and evaluate an automated content moderation gate using the `unitary/toxic-bert` model that flags toxic comments with at least 85% precision and 90% recall, preventing offensive language from distorting institutional facility ratings.

3. **Hybrid Aspect Category Extraction**:
   To engineer a hybrid topic extraction mechanism combining fast, deterministic domain keyword regular expressions with a multi-label DistilBERT topic model, achieving an aspect extraction F1-score exceeding 0.70 on unseen test comments.

4. **Context-Aware Aspect Sentiment Classification**:
   To fine-tune a DistilBERT model on educational and campus aspect-clause pairs, achieving an overall classification accuracy exceeding 90% and a macro-F1 score exceeding 0.85 across positive, neutral, and negative classes.

5. **Quantitative Metric Aggregation and Chronic Issue Detection**:
   To develop a transparent aggregation algorithm that converts sentiment distributions into standard 1.0 to 5.0 star ratings for every facility and aspect, and automatically identifies recurring chronic issues where negative sentiment equals or exceeds 70%.

6. **Fact-Checked Executive Summarization**:
   To integrate a locally hosted Large Language Model (LLaMA 3.1 via Ollama) capable of generating 2-to-3 sentence executive facility briefs, constrained by automated regex verification rules that reject hallucinated percentages or ungrounded topics with a template fallback.

7. **Offline Interactive Dashboard Deployment**:
   To build and deploy a responsive, fully offline web dashboard using Flask and Chart.js, providing college administrators with interactive ratings, chronic issue alerts, side-by-side facility comparisons, quarantined comment audits, and real-time inference for live student submissions.

---

## 2.4 Problem Statement

> *"Campus administrators in higher education institutions currently lack an automated, cost-effective, and robust system to transform large volumes of unstructured, informal, and multilingual (Tanglish) student feedback into transparent, aspect-specific ratings and actionable summaries. Existing manual processes are time-consuming and subjective, while commercial tools fail to handle dialectal slang, lack fine-grained aspect sentiment analysis, and allow abusive comments to distort quantitative metrics.*
>
> *Therefore, the problem is to engineer a unified, offline Natural Language Processing pipeline that filters toxic content, extracts granular facility aspects, classifies context-specific sentiment, calculates transparent 1.0 to 5.0 facility grades, alerts administrators to chronic recurring complaints, and generates verified executive summaries—all accessible through an intuitive, privacy-preserving web dashboard."*

---

## 2.5 Project Plan & Chronological Upgrade Story

The project was executed in a phased, iterative engineering progression. Rather than jumping directly into complex architectures, the team established baseline implementations for every component, measured their shortcomings, and progressively upgraded each module to state-of-the-art transformer and LLM approaches.

The chronological timeline of development is outlined below:

```
[Phase 1: Oct 19, 2026] ────> [Phase 2: Oct 22-23, 2026] ────> [Phase 3: Oct 24, 2026] ────> [Phase 4: Oct 25, 2026] ────> [Phase 5: Oct 27-29, 2026]
Data Synthesis &             Baseline Modules               Sentiment Upgrades &           Hybrid Aspects, Toxic-BERT   Dark-Mode Webapp,
Audit Verification           (VADER, TF-IDF LogReg)         Neutral Data Supplementation   & Local Ollama Summaries     Handoff & Pack Build
```

| Phase / Milestones | Target Dates (from Git logs & files) | Modules Built & Upgraded | Engineering Narrative & Key Decisions |
|---|---|---|---|
| **Phase 1: Dataset Generation & Audit** | 2026-10-19 | `merge_campus_data.py`<br>`split_data.py`<br>`validate_dataset.py` | Synthesized 800 campus comments across 16 batches for 8 facilities (`PROMPT.md`). Partitioned data into 70% Train (560), 15% Validation (120), and 15% Test (120) with zero leakage. Established immutable backups and data quality reports. |
| **Phase 2: Baseline Pipeline Construction** | 2026-10-22 to 2026-10-23 | `aspects.py` (v1)<br>`sentiment.py` (VADER)<br>`toxicity_baseline.py`<br>`aggregate.py` | Built rule-based keyword lexicon for aspect extraction (F1: 0.698). Implemented sentiment baseline using VADER augmented with a custom Tanglish word list (macro-F1: 0.687). Trained TF-IDF + Logistic Regression baseline on Jigsaw for abuse detection (F1: 0.741). Implemented 1-5 star ratings formula. |
| **Phase 3: Deep Learning Sentiment Upgrades** | 2026-10-24 | `colab_sentiment_distilbert.ipynb`<br>`neutral_additions.csv`<br>`sentiment_bert.py` | Trained DistilBERT v1 on EduRABSA (16,500 rows, macro-F1: 0.708). Fine-tuned DistilBERT v2 on campus train aspects (macro-F1: 0.829), but discovered neutral class suffered from severe sparsity (F1: 0.00). Supplemented dataset with 100 neutral comments (`neutral_additions.csv`). Trained DistilBERT v3, achieving robust 3-class classification (final test accuracy: 0.905, macro-F1: 0.875). |
| **Phase 4: Hybrid Aspects, Toxic-BERT & Ollama Summaries** | 2026-10-25 | `aspects_bert.py`<br>`aspects_hybrid.py`<br>`toxicity_bert.py`<br>`summarize.py`<br>`summarize_ai.py` | Trained multi-label DistilBERT topic model (`Aspect_extraction.ipynb`). Combined keyword regex with DistilBERT into a hybrid extractor (improved F1 from 0.698 to 0.742 on test set). Replaced baseline abuse detector with `unitary/toxic-bert` (precision jumped from 63% to 88%, false alarms dropped from 25 to 6). Integrated local Ollama runtime with LLaMA 3.1 and built automated regex fact-checking gate to prevent hallucinations. |
| **Phase 5: Full-Stack Webapp & Offline Deployment** | 2026-10-27 to 2026-10-29 | `webapp/app.py`<br>`webapp/static/`<br>`webapp/templates/`<br>`report_pack/` | Developed a fully offline Flask web application (`http://127.0.0.1:5000`) featuring dark-mode UI, persistent left sidebar, Chart.js graphs, clause routing for multi-facility comments, and real-time model inference. Completed end-to-end testing, documentation, and the complete academic handoff pack. |
