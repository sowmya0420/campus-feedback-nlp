"""Grid-search POS_T / NEG_T / NO_EVIDENCE_LABEL on VALIDATION only; prints best, writes nothing.
Copy the winning values into src/config.py by hand."""
import itertools
import numpy as np
from src.quick_check_sentiment import load, evaluate

df = load("validation")
rows = []
for p, n, ne in itertools.product(np.arange(0.05, 0.55, 0.05), np.arange(-0.55, -0.04, 0.05),
                                  ["neutral", "negative"]):
    rows.append((evaluate(df, p, n, ne)[1], round(p, 2), round(n, 2), ne))
rows.sort(reverse=True)
print("top 8 (macro-F1, POS_T, NEG_T, NO_EVIDENCE_LABEL):")
for r in rows[:8]:
    print(f"  {r[0]:.3f}  {r[1]:+.2f}  {r[2]:+.2f}  {r[3]}")
