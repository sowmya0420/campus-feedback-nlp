"""Where does the keyword-based aspect finder go wrong?
python -m src.aspect_errors              (train split: use this to study errors)
python -m src.aspect_errors validation   (sanity check: should match evaluate.py)"""
import json, random, sys
from collections import Counter
import pandas as pd
from src.aspects import extract_aspects

split = sys.argv[1] if len(sys.argv) > 1 else "train"
if split == "test":
    sys.exit("Keep the test split untouched until the very end.")
df = pd.read_csv(f"data/processed/{split}_comments.csv")

tp, fp, fn = Counter(), Counter(), Counter()
bad_terms = Counter()          # which keyword caused each false alarm
misses, extras = [], []
nothing_found = 0

for r in df.itertuples():
    gold = {a["category"] for a in json.loads(r.aspects)}
    found = {a["category"]: a["aspect_term"] for a in extract_aspects(r.text, r.facility)}
    found.pop("general", None)
    pred = set(found)
    for c in gold & pred:
        tp[(r.facility, c)] += 1
    for c in pred - gold:
        fp[(r.facility, c)] += 1
        bad_terms[(r.facility, c, found[c])] += 1
        extras.append((r.facility, c, found[c], r.text))
    for c in gold - pred:
        fn[(r.facility, c)] += 1
        misses.append((r.facility, c, sorted(pred), r.text))
        if not pred:
            nothing_found += 1

TP, FP, FN = sum(tp.values()), sum(fp.values()), sum(fn.values())
P, R = TP / (TP + FP), TP / (TP + FN)
print(f"{split}: {len(df)} comments | precision={P:.3f} recall={R:.3f} F1={2*P*R/(P+R):.3f}")
print(f"Correct {TP} | missed {FN} | false alarms {FP}")
print(f"Of the {FN} misses, {nothing_found} were comments where no keyword matched at all.")

keys = set(tp) | set(fp) | set(fn)
tab = pd.DataFrame([{"facility": f, "category": c, "correct": tp[(f, c)],
                     "missed": fn[(f, c)], "extra": fp[(f, c)]} for f, c in keys])
tab["errors"] = tab["missed"] + tab["extra"]
print("\nCategories with the most errors:")
print(tab.sort_values("errors", ascending=False).head(20).to_string(index=False))

print("\nKeywords that caused the most false alarms:")
for (f, c, t), n in bad_terms.most_common(15):
    print(f"  {n:3d}x  {f} / {c}  <- '{t}'")

rng = random.Random(0)
print("\nSample of MISSED aspects:")
for f, c, p, t in rng.sample(misses, min(25, len(misses))):
    print(f"  [{f}] missing '{c}' (found: {', '.join(p) or 'nothing'}) :: {t[:110]}")
print("\nSample of FALSE ALARMS:")
for f, c, term, t in rng.sample(extras, min(25, len(extras))):
    print(f"  [{f}] extra '{c}' via '{term}' :: {t[:110]}")