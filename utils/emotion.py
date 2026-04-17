"""
emotion.py
----------
Local NLP emotion detection using VADER (Valence Aware Dictionary and sEntiment Reasoner).
Runs entirely offline — no API calls, no cost.

Usage:
    from utils.emotion import detect_emotion
    result = detect_emotion("I feel really anxious today")
    # {"category": "Anxious", "score": -0.54, "emoji": "😟", "label": "Anxious", "color": "#fb923c"}
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Single analyzer instance loaded once at import time
_analyzer = SentimentIntensityAnalyzer()

# Crisis keywords mirror those in peacebot.py CRISIS_MARKERS
_CRISIS_WORDS = {
    "suicide",
    "kill myself",
    "end my life",
    "hurt myself",
    "self harm",
    "harm myself",
}

# Emotion category metadata used by the frontend for badge rendering
EMOTION_MAP: dict[str, dict] = {
    "Happy":   {"emoji": "🌿", "label": "Calm / Happy",    "color": "#4ade80"},
    "Neutral": {"emoji": "😐", "label": "Neutral",          "color": "#94a3b8"},
    "Anxious": {"emoji": "😟", "label": "Anxious",          "color": "#fb923c"},
    "Sad":     {"emoji": "💧", "label": "Sad",              "color": "#60a5fa"},
    "Angry":   {"emoji": "🔥", "label": "Angry / Stressed", "color": "#f87171"},
}


def detect_emotion(text: str) -> dict:
    """
    Analyse text and return an emotion category with metadata.

    Returns a dict with keys:
        category  (str)   — "Happy" | "Neutral" | "Anxious" | "Sad" | "Angry" | "Crisis"
        score     (float) — VADER compound score in [-1.0, 1.0]
        emoji     (str)   — representative emoji
        label     (str)   — human-readable label
        color     (str)   — hex colour for the frontend badge
    """
    if not text or not text.strip():
        return {"category": "Neutral", "score": 0.0, **EMOTION_MAP["Neutral"]}

    lowered = text.lower()

    # Crisis check takes priority over sentiment scoring
    if any(phrase in lowered for phrase in _CRISIS_WORDS):
        return {
            "category": "Crisis",
            "score":    -1.0,
            "emoji":    "🆘",
            "label":    "Crisis",
            "color":    "#dc2626",
        }

    # VADER compound score: >= 0.05 positive, <= -0.05 negative
    scores   = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        cat = "Happy"
    elif compound > -0.05:
        cat = "Neutral"
    else:
        if any(w in lowered for w in [
            "anxious", "anxiety", "panic", "worried",
            "overwhelmed", "fear", "nervous", "stress",
        ]):
            cat = "Anxious"
        elif any(w in lowered for w in [
            "angry", "anger", "furious", "mad",
            "irritated", "rage", "frustrated",
        ]):
            cat = "Angry"
        else:
            cat = "Sad"

    return {"category": cat, "score": round(compound, 3), **EMOTION_MAP[cat]}
