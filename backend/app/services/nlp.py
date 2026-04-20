"""
Simple NLP helpers for survey processing.
Currently provides sentiment analysis placeholder logic.
"""


def analyze_sentiment(text: str) -> dict:
    """
    Very simple sentiment estimation for Phase 1.
    Returns:
    {
      "label": "negative" | "neutral" | "positive",
      "score": float
    }
    """
    lower_text = text.lower()

    negative_keywords = [
        "problem", "contaminated", "shortage", "sick", "urgent",
        "critical", "bad", "difficult", "no water", "no food",
        "disease", "malnutrition", "failing", "flood", "damage"
    ]
    positive_keywords = [
        "good", "improved", "better", "support", "helped", "safe"
    ]

    neg_hits = sum(1 for word in negative_keywords if word in lower_text)
    pos_hits = sum(1 for word in positive_keywords if word in lower_text)

    if neg_hits > pos_hits:
        return {"label": "negative", "score": round(min(1.0, 0.2 + neg_hits * 0.1), 2)}
    if pos_hits > neg_hits:
        return {"label": "positive", "score": round(min(1.0, 0.2 + pos_hits * 0.1), 2)}

    return {"label": "neutral", "score": 0.5}
