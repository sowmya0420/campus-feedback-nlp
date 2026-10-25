"""DistilBERT aspect model: how likely is each topic to be mentioned in a comment?"""
import json, os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

DIR = "models/aspect_distilbert_v1"
_tok = _model = _meta = _id = None

def _load():
    global _tok, _model, _meta, _id
    if _model is None:
        _tok = AutoTokenizer.from_pretrained(DIR)
        _model = AutoModelForSequenceClassification.from_pretrained(DIR).eval()
        _meta = json.load(open(os.path.join(DIR, "labels.json")))
        _id = {c: i for i, c in enumerate(_meta["labels"])}

def topic_probs(texts, facilities):
    """-> one dict per comment: {category: probability}, only topics valid for that facility."""
    _load()
    inputs = [f"{f.replace('_', ' ')}: {t}" for f, t in zip(facilities, texts)]
    out = []
    for i in range(0, len(inputs), 32):
        enc = _tok(inputs[i:i + 32], truncation=True, max_length=96, padding=True, return_tensors="pt")
        with torch.no_grad():
            p = torch.sigmoid(_model(**enc).logits).numpy()
        for row, f in zip(p, facilities[i:i + 32]):
            out.append({c: float(row[_id[c]]) for c in _meta["valid"].get(f, [])})
    return out