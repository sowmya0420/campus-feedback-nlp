import json, sys
import pandas as pd
from src.aspects import extract_aspects

split = sys.argv[1] if len(sys.argv) > 1 else "train"
df = pd.read_csv(f"data/processed/{split}_comments.csv")

tp = fp = fn = 0
misses = []
for _, r in df.iterrows():
    gold = {a["category"] for a in json.loads(r["aspects"])}
    pred = {a["category"] for a in extract_aspects(r["text"], r["facility"])} - {"general"}
    tp += len(gold & pred); fp += len(pred - gold); fn += len(gold - pred)
    if gold != pred:
        misses.append((r["facility"], r["text"], sorted(gold), sorted(pred)))

p = tp / (tp + fp) if tp + fp else 0
rc = tp / (tp + fn) if tp + fn else 0
f1 = 2 * p * rc / (p + rc) if p + rc else 0
print(f"{split}: precision={p:.3f} recall={rc:.3f} F1={f1:.3f}  ({len(misses)}/{len(df)} comments differ)")
for m in misses[:15]:
    print("\n", m[0], "|", m[1], "\n   gold:", m[2], "\n   pred:", m[3])