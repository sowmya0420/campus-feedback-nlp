from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

LABELS = ["positive", "neutral", "negative"]   # index 0, 1, 2

texts = [
    "The library closes at 8 PM.",
    "The Wi-Fi is excellent.",
    "The hostel bathrooms are dirty and smell terrible.",
    "The food is okay, nothing special.",
    "The bus timing is average.",
    "The classrooms are clean and well lit.",
]

folders = [
    "models/sentiment_distilbert",
    "models/sentiment_distilbert_v2",
    "models/sentiment_distilbert_v3",
]

for folder in folders:
    tokenizer = AutoTokenizer.from_pretrained(folder)
    model = AutoModelForSequenceClassification.from_pretrained(folder).eval()
    print(f"\nMODEL: {folder}")

    for sentence in texts:
        inputs = tokenizer(
            "general", sentence,
            return_tensors="pt", truncation=True, max_length=128
        )
        with torch.no_grad():
            probs = torch.softmax(model(**inputs).logits, dim=-1)[0].tolist()
        best = max(range(len(probs)), key=probs.__getitem__)
        shown = "  ".join(f"{LABELS[i]} {probs[i]:.2f}" for i in range(len(probs)))
        print(f"  {LABELS[best]:<9} <- {sentence}")
        print(f"      ({shown})")