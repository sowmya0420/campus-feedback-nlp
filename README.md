# NLP-Based Campus Facility Feedback Analysis System

Reads student comments about campus facilities and turns them into something a college can act on: which comments are abusive, what each comment is about, how students feel about each topic, and a rating, a list of recurring issues and a short written summary for every facility. A Streamlit dashboard shows the results.

**Facilities covered:** canteen, classrooms, hostel mess, hostel rooms, labs, library, transport, wifi.
**Data:** 800 synthetic campus comments (560 train, 120 validation, 120 test), 48 of them abusive. Many comments mix English and Tamil-English (Tanglish).

## How it works

For every comment, `src/pipeline.py` does the following:

1. **Abuse detection.** `unitary/toxic-bert` flags abusive comments (cutoff 0.5). Flagged comments are kept out of the ratings.
2. **Topic finding.** A keyword matcher finds topics and the exact part of the sentence. A DistilBERT model adds topics the keywords missed when it is at least 50% sure (`src/aspects_hybrid.py`).
3. **Sentiment.** A DistilBERT model judges positive, neutral or negative for each topic.
4. **Ratings and issues.** `src/aggregate.py` turns the results into a 1 to 5 rating per facility and topic, and lists topics that are mostly negative (`ISSUE_NEG_SHARE = 0.7` in `src/config.py`).
5. **Summaries.** A local AI model (llama3.1 through Ollama) writes a short summary per facility from the numbers. An automatic check rejects summaries that use numbers or topics that are not in the facts, and a template summary is the fallback.

## Results

| Part | Result | Measured on |
|---|---|---|
| Abuse detection (toxic-bert) | precision 88%, recall 90%, F1 0.89 | all 800 campus comments |
| Abuse detection (old baseline) | precision 63%, recall 90%, F1 0.74 | all 800 campus comments |
| Topic finding (keywords + DistilBERT) | F1 0.742 | test split |
| Topic finding (keywords only / model only) | F1 0.698 / 0.656 | validation split |
| Sentiment | accuracy 0.905, macro-F1 0.875 | test split, correct topics given |
| Summaries | 8 of 8 written by the AI, read against the ratings, 2 corrected by hand | all facilities |

The test split was evaluated once, at the end. Cutoffs and settings were chosen on the validation split.

## Project structure

```
src/
  pipeline.py            single entry point: analyse(text, facility)
  aspects.py             keyword topic finder
  aspects_bert.py        DistilBERT topic model
  aspects_hybrid.py      keywords + model, used by the pipeline
  sentiment.py           sentiment prediction
  sentiment_bert.py      DistilBERT sentiment model loading
  toxicity_baseline.py   old abuse detector (TF-IDF + logistic regression)
  toxicity_bert.py       toxic-bert scoring and evaluation
  compare_toxicity.py    side-by-side comparison of the two abuse detectors
  aggregate.py           ratings.csv and issues.csv
  summarize.py           writes summaries.csv (with checks and fallback)
  summarize_ai.py        Ollama call
  aspect_errors.py       error analysis of the keyword topic finder
  evaluate.py            validation and test evaluation
  config.py              paths and settings
data/
  processed/             train, validation and test comment files
  outputs/               predictions, ratings, issues, summaries
models/                  not in the repository (see below)
```

## Setup

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Models (not included in the repository)

| Model | Where it comes from |
|---|---|
| `models/sentiment_distilbert_v3` | trained on Colab (see `notebooks/`) |
| `models/aspect_distilbert_v1` | trained on Colab (see `notebooks/`), includes `labels.json` |
| `unitary/toxic-bert` | downloads automatically on first run (about 440 MB, needs internet) |
| `models/toxicity_tfidf_logreg.joblib` | created by `python -m src.toxicity_baseline`, only needed for the comparison |

Set the sentiment model folder with `BERT_MODEL_DIR` in `src/config.py`.

### Summaries (optional)

Install [Ollama](https://ollama.com) and run `ollama pull llama3.1`. If Ollama is not running, the template summary is used instead.

### Extra data (only for retraining or comparison)

The old abuse baseline needs the Jigsaw `train.csv` in `data/external/jigsaw/`. `src/download_edurabsa.py` downloads the EduRABSA benchmark.

## Running

```
python -m src.pipeline            # analyse all comments -> data/outputs/predictions.csv
python -m src.aggregate           # -> ratings.csv, issues.csv
python -m src.summarize           # -> summaries.csv (needs Ollama for AI summaries)
streamlit run <path to dashboard file>
python -m src.evaluate validation
```

Warning: `src.summarize` overwrites `data/outputs/summaries.csv`, including any hand corrections. `python -m src.evaluate test --final` is meant to be run once, at the very end.

## Known limits

- Mild insults aimed at a person (for example "clown") are missed by both abuse detectors.
- toxic-bert sometimes flags harsh hygiene complaints ("disgusting", "dirty") as abuse.
- Topics found only by the model are judged on the whole comment, which is less precise when a comment mixes good and bad points.
- The topic model was trained on only 560 comments, and some labels are debatable.
- The data is synthetic and has only 48 abusive comments, so recall numbers are indicative, not exact.
- The Summaries page is static. An interactive version is planned.
