from datasets import load_dataset
import os

os.makedirs("data/external/edurabsa", exist_ok=True)

ds = load_dataset("yhua219/EduRABSA_ASQE")
print(ds)  # should show train (~4,000 rows) and test (~2,500 rows)

# save a local copy so you never need to re-download
ds["train"].to_json("data/external/edurabsa/train.jsonl")
ds["test"].to_json("data/external/edurabsa/test.jsonl")
print("Saved.")