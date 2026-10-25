"""Aspect finding = keyword matcher + DistilBERT additions.
Keywords find the topic and the exact part of the sentence. The model adds topics the
keywords missed, but only when it is at least ADD_CONF sure."""
from src.aspects import extract_aspects as keyword_aspects
from src.aspects_bert import topic_probs

ADD_CONF = 0.5

def extract_aspects(text, facility):
    found = keyword_aspects(text, facility)
    real = [a for a in found if a["category"] != "general"]
    have = {a["category"] for a in real}
    probs = topic_probs([str(text)], [facility])[0]
    extra = [c for c, v in probs.items() if v >= ADD_CONF and c not in have]
    if not extra:
        return found
    # topics found only by the model have no keyword, so the sentiment model reads the whole comment
    return real + [{"aspect_term": None, "category": c, "clause": str(text)} for c in extra]