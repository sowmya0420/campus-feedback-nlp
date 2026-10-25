"""Keywords only / model only / hybrid, on VALIDATION (the test split stays untouched).
python -m src.aspect_hybrid_eval"""
import json, itertools
import pandas as pd
from src.aspects import extract_aspects
from src.aspects_bert import topic_probs

df = pd.read_csv("data/processed/validation_comments.csv")
gold = [{a["category"] for a in json.loads(s)} for s in df.aspects]
kw = [{a["category"] for a in extract_aspects(t, f)} - {"general"} for t, f in zip(df.text, df.facility)]
pr = topic_probs(list(df.text), list(df.facility))

def score(preds):
    tp = sum(len(g & p) for g, p in zip(gold, preds))
    fp = sum(len(p - g) for g, p in zip(gold, preds))
    fn = sum(len(g - p) for g, p in zip(gold, preds))
    P = tp / (tp + fp) if tp + fp else 0
    R = tp / (tp + fn)
    return P, R, (2 * P * R / (P + R) if P + R else 0)

def show(name, preds):
    P, R, F = score(preds)
    print(f"{name:42s} P={P:.3f} R={R:.3f} F1={F:.3f}")

show("keywords only", kw)
show("model only (confidence >= 0.2)", [{c for c, v in d.items() if v >= 0.2} for d in pr])

print("\nHybrid. KEEP = a keyword hit survives only if the model's confidence is at least this.")
print("ADD = also accept topics the model alone is this sure about (1.1 = never add).")
rows = []
for keep, add in itertools.product([0.0, 0.05, 0.1, 0.2], [0.3, 0.4, 0.5, 0.6, 1.1]):
    preds = [{c for c in k if d.get(c, 0) >= keep} | {c for c, v in d.items() if v >= add}
             for k, d in zip(kw, pr)]
    P, R, F = score(preds)
    rows.append((F, keep, add, P, R))
for F, keep, add, P, R in sorted(rows, reverse=True)[:8]:
    print(f"  KEEP>={keep:<4} ADD>={add:<4} P={P:.3f} R={R:.3f} F1={F:.3f}")