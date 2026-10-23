"""Loads the Colab-trained DistilBERT (models/sentiment_distilbert) and predicts sentiment
for (aspect term, clause). Needs: pip install torch transformers"""
import torch
from src import config
from transformers import AutoTokenizer, AutoModelForSequenceClassification

LABELS = ["positive", "neutral", "negative"]
_tok = _model = None

def _load():
    global _tok, _model
    if _model is None:
        path = getattr(config, "BERT_MODEL_DIR", "models/sentiment_distilbert")
        _tok = AutoTokenizer.from_pretrained(path)
        _model = AutoModelForSequenceClassification.from_pretrained(path).eval()

def predict_sentiment_bert(clause, aspect_term=None):
    _load()
    enc = _tok(str(aspect_term or "general"), str(clause), truncation=True, max_length=128, return_tensors="pt")
    with torch.no_grad():
        return LABELS[int(_model(**enc).logits.argmax(dim=-1))]
