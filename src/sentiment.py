"""Aspect-level sentiment baseline: VADER + campus/Tanglish word list.
Scores the CLAUSE that contains the aspect, not the whole comment."""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.preprocess import clean_text, tokenize
from src import config

# word -> valence (VADER scale about -4..+4)
CAMPUS_WORDS = {
    # negative (English)
    "broken": -2.5, "dirty": -2.5, "unclean": -2.5, "unhygienic": -2.8, "stale": -2.5,
    "oily": -1.8, "undercooked": -2.5, "slow": -2.0, "lag": -1.8, "lagging": -2.0,
    "hang": -1.8, "hangs": -2.0, "crowded": -1.8, "overcrowded": -2.5, "costly": -2.0,
    "expensive": -2.0, "overpriced": -2.5, "delayed": -2.0, "late": -1.6, "leaking": -2.2,
    "leak": -2.0, "faulty": -2.5, "outdated": -2.0, "missing": -2.0, "unavailable": -2.0,
    "rude": -2.8, "rash": -2.5, "pathetic": -3.0, "horrible": -3.0, "terrible": -3.0,
    "worst": -3.2, "waste": -2.2, "scratches": -1.5, "graffiti": -1.5, "stained": -1.8,
    "dusty": -1.8, "dust": -1.4, "smell": -1.5, "noisy": -2.0, "stuffy": -1.8,
    "unsafe": -2.5, "dim": -1.4, "wobbly": -1.8, "clogged": -2.0, "irritate": -2.0,
    "irritating": -2.2, "nothing": -1.2, "never": -1.2, "poor": -2.3, "bad": -2.3,
    "insufficient": -2.0, "limited": -1.3, "disconnects": -2.2, "drops": -1.6,
    "unstable": -2.2, "throttling": -2.0, "buffer": -1.5, "buffering": -2.0,
    "timeouts": -2.0, "timeout": -2.0, "hike": -1.5, "shouts": -2.2, "shouting": -2.2,
    "cramped": -2.0, "congested": -2.0, "tiny": -1.5, "cockroach": -2.8, "cockroaches": -2.8,
    "insects": -2.5, "worms": -2.8, "worm": -2.8, "hair": -1.5, "flies": -1.8,
    "ignored": -2.2, "ignore": -2.0, "nobody": -1.3, "unreliable": -2.3, "ruined": -2.5,
    "fools": -2.8, "shit": -3.0, "useless": -2.8, "tasteless": -2.5, "bland": -1.8,
    "monotonous": -2.0, "repeat": -1.2, "repeated": -1.2, "rejected": -1.8, "freezes": -2.0,
    "congestion": -1.8, "overspeeding": -2.5, "accident": -2.2, "accidents": -2.2,
    # positive (English)
    "clean": 2.0, "tasty": 2.5, "fresh": 2.0, "delicious": 3.0, "crispy": 2.0,
    "helpful": 2.5, "polite": 2.3, "friendly": 2.3, "punctual": 2.3, "fast": 2.0,
    "spacious": 2.0, "cheap": 1.8, "affordable": 2.0, "reasonable": 1.6, "fair": 1.5,
    "quiet": 1.8, "peaceful": 2.0, "comfortable": 2.0, "smooth": 1.8, "smoothly": 1.8,
    "stable": 1.8, "reliable": 2.2, "strong": 1.8, "improved": 2.0, "bright": 1.5,
    "cool": 1.5, "pleasant": 2.2, "homely": 2.2, "filling": 1.5, "saved": 1.8,
    "smiled": 2.0, "safe": 2.0, "secure": 1.8, "well": 1.3, "maintained": 1.5,
    "supportive": 2.3, "good": 2.0, "gud": 2.0, "nice": 2.0, "best": 3.0, "great": 2.8,
    "excellent": 3.0, "perfect": 2.8, "satisfied": 2.2, "amazing": 3.0, "lyk": 1.5,
    "available": 1.0, "extended": 1.2, "open": 0.8, "enough": 1.0, "variety": 0.8,
    "recommended": 1.8, "worth": 1.5, "prompt": 1.8, "quick": 1.8, "quickly": 1.8,
    # Tanglish
    "nalla": 2.2, "nallaa": 2.2, "semma": 3.0, "super": 2.5, "supera": 2.5, "mass": 2.0,
    "mokka": -2.5, "waste": -2.2, "kevalam": -3.0, "romba": 0.0, "illa": -1.5, "illai": -1.5,
    "seri": 0.5, "sooper": 2.5, "worstu": -3.0, "pidikala": -2.2, "kammi": -1.8,
    "athigam": -1.2, "late": -1.6, "kasta": -1.8, "kashtam": -1.8, "nalladhu": 2.0,
}
# round-1 fixes from train errors (frozen after this)
CAMPUS_WORDS.update({"queue": -1.5, "endless": -2.5, "less": -1.2, "raw": -2.0, "jaasthi": -2.0,
    "expnsive": -2.0, "waitng": -1.5, "wait": -1.2, "waiting": -1.2, "mixed": -1.5, "half": -0.8,
    "unnecessarily": -1.5, "huge": 0.5, "wiped": 1.2, "promptly": 1.5, "cleaner": 1.5,
    "extra": 0.8, "healthy": 0.5, "needed": -1.2, "need": -1.2, "run": -0.6, "gets": 0.0,
    "average": -0.6, "very": 0.0, "tastes": 0.0, "soup": -0.8, "mattum": -0.5, "romba": -0.3})
# words VADER treats as strongly positive but which are neutral/negative in campus talk
OVERRIDES = {"issue": -1.5, "issues": -1.8, "problem": -2.0, "problems": -2.2, "complaint": -1.8,
             "complaints": -1.8, "without": -0.8, "lack": -2.0,
             "lacks": -2.0, "lacking": -2.0, "free": 0.3, "support": 0.8}

_an = SentimentIntensityAnalyzer()
_an.lexicon.update(CAMPUS_WORDS)
_an.lexicon.update(OVERRIDES)


def score_clause(clause):
    return _an.polarity_scores(clean_text(clause))["compound"]


def label_from_score(s, pos_t=None, neg_t=None, no_evidence=None):
    """no_evidence: label for clauses where no sentiment word fired (score exactly 0).
    Tuned on validation: in complaint-heavy feedback a bare mention is usually a complaint."""
    pos_t = config.POS_T if pos_t is None else pos_t
    neg_t = config.NEG_T if neg_t is None else neg_t
    no_evidence = config.NO_EVIDENCE_LABEL if no_evidence is None else no_evidence
    if s == 0.0:
        return no_evidence
    return "positive" if s >= pos_t else "negative" if s <= neg_t else "neutral"


def predict_sentiment(clause, aspect_term=None):
    """Same call for both backends; switch with config.SENTIMENT_BACKEND."""
    if config.SENTIMENT_BACKEND == "distilbert":
        from src.sentiment_bert import predict_sentiment_bert
        return predict_sentiment_bert(clause, aspect_term)
    return label_from_score(score_clause(clause))
