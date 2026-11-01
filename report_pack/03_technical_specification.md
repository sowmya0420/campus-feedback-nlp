# Chapter 3: Technical Specification

This document provides the complete material for **Chapter 3** of the project report, detailing the functional and non-functional requirements, technical/economic/social feasibility studies, and exact real-world hardware and software specifications.

---

## 3.1 System Requirements

### 3.1.1 Functional Requirements

Functional requirements define the core operational behaviors and features that the system must perform:

1. **Text Ingestion and Slang Normalization (FR-01)**:
   - The system shall accept raw, free-form student feedback in English and Tamil-English (Tanglish) via batch CSV files or an interactive text area.
   - The system shall automatically lowercase text, normalize stretched letters (e.g., converting `"sooooo"` to `"soo"`), strip irregular punctuation, and resolve colloquial slang terms using a domain lexicon.

2. **Clause-Level Segmentation (FR-02)**:
   - The system shall divide multi-sentence comments into distinct semantic clauses based on punctuation delimiters (`;`, `,`, `!`, `?`, `.`) and contrast transition words (`but`, `however`, `though`, `although`, `yet`, and Tanglish markers `aana`, `aanaal`, `anaal`).

3. **Automated Abusive Content Screening (FR-03)**:
   - The system shall evaluate incoming comments using the `unitary/toxic-bert` model.
   - Comments receiving a maximum toxicity score equal to or exceeding the threshold ($\tau = 0.50$) shall be marked as `abusive: true` and immediately quarantined from facility ratings.
   - Quarantined comments shall be logged in a dedicated moderation table displaying the toxicity score and truncated text for administrative audit.

4. **Multi-Facility Clause Routing (FR-04)**:
   - In "All facilities" mode, the system shall analyze each subclause independently and assign it to the appropriate campus facility based on keyword matching, clause carry-over, and hostel disambiguation rules (e.g., routing *"Wi-Fi drops in the hostel"* to Wi-Fi rather than Hostel Rooms).
   - If a clause mentions an aspect with no facility anchor (e.g., *"The food is great but prices are high"*), the system shall label it as `"Facility not stated"` and display ambiguous candidate facilities (e.g., *"fits Canteen, Hostel Mess"*).

5. **Hybrid Aspect Category Extraction (FR-05)**:
   - The system shall extract aspect terms and assign them to one of 42 predefined categories using a compiled regular expression keyword lexicon.
   - If the keywords miss aspects that the DistilBERT multi-label topic model predicts with at least 50% confidence (`ADD_CONF = 0.50`), the system shall append those additional categories to the extracted list.

6. **Aspect-Level Sentiment Classification (FR-06)**:
   - The system shall feed the pair `[aspect term]` + `[subclause]` into the fine-tuned DistilBERT v3 model.
   - The model shall classify each aspect into one of three distinct polarities: `positive`, `neutral`, or `negative`.

7. **Quantitative Star Rating Computation (FR-07)**:
   - The system shall compute an overall facility rating and individual aspect ratings on a standard 1.0 to 5.0 star scale using the formula:
     $$\text{Rating} = 1 + 4 \times \frac{\text{positive} + 0.5 \times \text{neutral}}{\text{total mentions}}$$
   - All computed ratings shall be rounded to two decimal places.

8. **Recurring Chronic Issue Detection (FR-08)**:
   - The system shall flag any aspect as a "recurring chronic issue" if its negative mention share equals or exceeds 70% (`ISSUE_NEG_SHARE = 0.70`) and it has at least 5 total mentions (`ISSUE_MIN_MENTIONS = 5`).

9. **Factual Executive Summary Generation (FR-09)**:
   - The system shall feed aggregated facility metrics into a local LLaMA 3.1 language model via Ollama to generate a 2-to-3 sentence executive brief.
   - The system shall run an automated regex fact-checking function (`looks_wrong`) to ensure that all cited percentages and aspect categories exist in the factual input. If any hallucination is detected across 3 attempts, it shall automatically fall back to a deterministic template summary.

10. **Interactive Offline Visualization (FR-10)**:
    - The system shall render an offline web application providing an Executive Home view, Live Feedback Demo, Facility Explorer, Aspect Ratings Chart & Table, Ranked Recurring Issues, Facility Briefs with Compare Mode, and Abusive Content Moderation.

---

### 3.1.2 Non-Functional Requirements

Non-functional requirements describe the quality attributes, usability, security, and performance constraints of the system:

1. **Inference Speed & Latency**:
   - For batch execution, the pipeline shall process all 800 campus comments through abuse detection, aspect extraction, and sentiment classification in under 60 seconds on a standard multi-core CPU.
   - In the interactive web application, real-time live demo inference for a single comment shall return within 500 milliseconds for classification, and within 3 to 5 seconds if live Ollama AI summarization is invoked.

2. **Full Offline Autonomy & Zero External Network Dependencies**:
   - The entire production web application (`webapp/app.py`) and inference pipeline shall run 100% locally and offline without requiring active internet connectivity.
   - All client-side fonts (Inter font family), icons (inline SVG), and charting libraries (Chart.js v4.4.7) shall be bundled locally within `webapp/static/`, eliminating dependencies on external Content Delivery Networks (CDNs).
   - Machine learning models and tokenizer weights shall load locally from disk (`models/` and Hugging Face local cache) with offline environment flags enabled (`HF_HUB_OFFLINE = 1`, `TRANSFORMERS_OFFLINE = 1`).

3. **High Classification Accuracy & Balanced Robustness**:
   - The aspect-based sentiment classifier shall maintain an overall accuracy exceeding 90% and a macro-F1 score exceeding 0.85 across all three classes, preventing bias toward negative complaints.
   - The abuse detection gate shall achieve a precision of at least 85% to minimize false alarms on harsh but legitimate facility complaints.

4. **Data Integrity & Student Privacy**:
   - The system shall preserve strict student anonymity. No personally identifiable information (PII) such as student names, registration numbers, IP addresses, or email accounts shall ever be recorded, processed, or logged.
   - Ground truth datasets and prediction outputs in `data/outputs/` shall be accessed in read-only mode by the web application to prevent accidental data corruption.

5. **User Experience & Accessibility**:
   - The dashboard interface shall feature a high-contrast dark theme (background `#0e1013`, cards `#181b21`, text `#e8eaed`) designed to minimize eye fatigue during extended administrative reviews.
   - All charts and data tables shall be responsive, fitting standard laptop and desktop screens (1366x768 and 1920x1080) without horizontal page overflow.

---

## 3.2 Feasibility Study

### 3.2.1 Technical Feasibility
The technical feasibility evaluates whether the system can be developed and operated using current technologies, available libraries, and engineering expertise:
- **Maturity of Open-Source Frameworks**: The project leverages mature, production-grade open-source libraries including PyTorch, Hugging Face Transformers, Scikit-Learn, and Flask. These frameworks provide stable APIs, comprehensive documentation, and broad community support.
- **Feasibility of Compact Transformers**: By selecting DistilBERT (66 million parameters) rather than massive multi-billion parameter models for core classification, the pipeline achieves deep semantic comprehension while remaining lightweight enough to run inference on ordinary CPU hardware without requiring dedicated enterprise GPU servers.
- **Local Large Language Model Feasibility**: The integration of Ollama enables local execution of quantized 8-billion parameter models (LLaMA 3.1) on local hardware. The inclusion of an automated regex-based fallback mechanism guarantees that the system never breaks or outputs hallucinated numbers even if the local LLM encounters resource limits.
- **Conclusion**: The technical implementation is completely feasible, robust, and proven through reproducible project execution.

### 3.2.2 Economic Feasibility
The economic feasibility examines the financial investment, development expenses, and operational overhead required to deploy and maintain the system:
- **Zero Software Licensing Cost**: Every tool and software component utilized—Python 3.11, PyTorch, Hugging Face Transformers, Flask, Streamlit, and Chart.js—is open-source and released under permissive licenses (Apache 2.0, MIT, or BSD). No commercial software licenses are required.
- **Zero Cloud API Subscription Fees**: Unlike commercial solutions that charge per-token or per-request fees (such as OpenAI GPT-4, Google Cloud NLP, or AWS Comprehend), this system runs entirely on local pre-trained and fine-tuned models. There are **zero recurring API billing costs**.
- **Free-Tier Training Infrastructure**: All deep learning model training and hyperparameter tuning were conducted using the standard free tier of Google Colab (utilizing a complimentary NVIDIA Tesla T4 GPU). No paid cloud compute or specialized hardware clusters were purchased.
- **Minimal Hardware Investment**: The production application runs smoothly on standard university desktop computers and existing administrative laptops without requiring specialized GPU hardware.
- **Conclusion**: The economic feasibility is outstanding. The total financial expenditure incurred during development was **₹0.00 ($0.00)**.

### 3.2.3 Social and Institutional Feasibility
The social feasibility evaluates the broader organizational benefits, user acceptance, and impact on campus stakeholders:
- **Benefits to Students**: Students gain a direct, anonymous, and trusted channel to voice facility grievances without fear of academic reprisal. By analyzing feedback objectively at the aspect level, students can see tangible evidence that their specific complaints (such as dining hall hygiene or broken lab computers) are recognized rather than lost in broad statistical averages.
- **Benefits to Campus Administration**: Facility managers, hostel wardens, and institutional leaders receive clean, actionable intelligence. Instead of sifting through hundreds of unorganized emails or papers, they receive clear 1-to-5 star grades, immediate alerts on chronic recurring issues, and verified 3-sentence executive summaries suitable for management meetings.
- **Protection of Campus Staff**: The automated toxic language quarantine prevents unfair personal harassment from penalizing canteen workers, bus drivers, or custodial staff in quantitative evaluations, fostering a fair and respectful workplace environment.
- **Conclusion**: The system demonstrates strong social feasibility and provides immediate institutional value to university governance.

---

## 3.3 System Specification

### 3.3.1 Hardware Specification

To ensure absolute factual precision, the hardware specifications below are separated into the real local development machine (read directly from the physical host system) and the cloud training environment:

#### 1. Local Development and Deployment Computer (Verified System Specifications):
- **Computer Architecture**: AMD64 (x86_64)
- **Operating System**: Microsoft Windows 10 / Windows 11 Education/Pro (OS Build: 10.0.26300)
- **Central Processing Unit (CPU)**: GenuineIntel Intel64 Family 6 Model 154 Stepping 4 (12th/13th Generation Intel Core Mobile Processor architecture)
  - *Logical CPU Cores*: 12 Cores
- **Physical System Memory (RAM)**: 15.68 GB (16.0 GB Total Physical RAM)
- **Local Storage**: Solid State Drive (SSD) with at least 5.0 GB available space for model weights and environment storage.
- **Local Model Storage Footprint**:
  - `unitary/toxic-bert` weights: ~440 MB
  - `models/sentiment_distilbert_v3` fine-tuned weights: ~268 MB
  - `models/aspect_distilbert_v1` weights: ~268 MB
  - `models/toxicity_tfidf_logreg.joblib` baseline model: ~8.8 MB

#### 2. Cloud Model Training Environment (Google Colab - Verified from Notebook Logs):
- **Platform**: Google Colaboratory (Free Tier)
- **Graphics Processing Unit (GPU)**: NVIDIA Tesla T4 GPU
- **GPU Memory (VRAM)**: 16 GB GDDR6
- **CUDA Support**: CUDA Version 12.x enabled (`torch.cuda.is_available() == True`)
- **Precision Mode**: Mixed Precision FP16 enabled (`fp16=True`) for fast tensor operations.

---

### 3.3.2 Software Specification

The software environment, development tools, and exact library versions installed in the project virtual environment (`venv`) are documented below:

#### 1. Programming Language and Core Runtime:
- **Python Version**: `Python 3.11.5` (64-bit)

#### 2. Machine Learning, Deep Learning, and NLP Libraries (Exact Versions from `pip list`):
- `torch`: **2.14.1** (PyTorch deep learning tensor computing and neural network runtime)
- `transformers`: **5.20.2** (Hugging Face transformer architectures and pipelines)
- `tokenizers`: **0.23.3** (Fast sub-word tokenization engine)
- `safetensors`: **0.8.0** (Fast, secure neural network weight serialization)
- `scikit-learn`: **1.9.1** (Machine learning algorithms, TF-IDF vectorization, Logistic Regression, evaluation metrics)
- `vaderSentiment`: **3.3.2** (Valence Aware Dictionary for sEntiment Reasoning, used in baseline)
- `joblib`: **1.6.0** (Model serialization and disk persistence)

#### 3. Data Processing and Mathematics:
- `pandas`: **3.0.6** (Dataframe manipulation, CSV ingestion, aggregation)
- `numpy`: **2.4.6** (Numerical array mathematics and vector operations)
- `scipy`: **1.17.1** (Scientific computing and statistical routines)

#### 4. Web Application Frameworks and Server Runtime:
- `Flask`: **3.1.3** (Lightweight WSGI web application framework powering the primary dashboard)
- `Werkzeug`: **3.1.9** (WSGI web server and routing utilities)
- `Jinja2`: **3.1.6** (Template engine for dynamic HTML rendering)
- `streamlit`: **1.66.1** (Rapid interactive data application framework used for prototype dashboard)
- `plotly`: **7.1.0** (Interactive charting engine used inside the Streamlit dashboard)
- `requests`: **2.34.2** (HTTP client for querying the local Ollama REST endpoint)

#### 5. Local Large Language Model (LLM) Server:
- **Ollama Engine**: Version 0.3.x+ running locally as a background service on `http://localhost:11434`
- **Hosted Model**: `llama3.1` (8-Billion parameter instruction-tuned model, quantized 4-bit)

#### 6. Client-Side Presentation and UI Assets (100% Offline in `webapp/static/`):
- **Charting Engine**: `Chart.js v4.4.7` (bundled locally in `webapp/static/js/chart.umd.min.js`)
- **Typography**: `Inter` Web Font family (weights 400, 500, 600, 700 bundled in `webapp/static/fonts/inter-*.woff2`)
- **Iconography**: Custom outline SVG icons stored locally in `webapp/static/icons/`
- **Styling**: Custom responsive CSS (`webapp/static/css/style.css`) implementing dark-theme variables.

#### 7. Development Tools and Integrated Development Environments (IDEs):
- **Primary IDE**: Visual Studio Code (VS Code) with Python and PowerShell extensions
- **Cloud Computing IDE**: Google Colaboratory (Jupyter Notebook interface)
- **Version Control System**: Git version 2.x, hosted on GitHub repository `https://github.com/sowmya0420/campus-feedback-nlp`
