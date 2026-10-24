"""Central settings. Stages import from here; nothing is hardcoded elsewhere."""
POS_T = 0.05          # compound >= POS_T -> positive   (tuned on VALIDATION)
NEG_T = -0.05         # compound <= NEG_T -> negative   (tuned on VALIDATION)
NO_EVIDENCE_LABEL = "negative"   # tuned on VALIDATION: "neutral" or "negative"
ISSUE_NEG_SHARE = 0.7   # aspect is a recurring issue if >=40% of its mentions are negative
ISSUE_MIN_MENTIONS = 5
SEED = 42

# "lexicon" = VADER + word list (baseline) | "distilbert" = model trained on Colab (models/sentiment_distilbert)
SENTIMENT_BACKEND = "distilbert"
BERT_MODEL_DIR = "models/sentiment_distilbert_v3"
