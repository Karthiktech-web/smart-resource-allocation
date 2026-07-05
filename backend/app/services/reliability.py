"""Compute NGO reliability scores from task outcomes and feedback."""
from typing import Any

SMOOTHING = 0.7


def update_score(current: float, rating: float, tasks_completed: int) -> float:
    """Blend the current 0..100 reliability score with a new 1..5 star rating."""
    rating_pct = max(0.0, min(5.0, rating)) / 5.0 * 100.0
    smoothing = min(SMOOTHING, 0.3 + tasks_completed * 0.05)
    return round(smoothing * current + (1 - smoothing) * rating_pct, 2)


def completion_rate(tasks_completed: int, tasks_total: int) -> float:
    if tasks_total <= 0:
        return 0.0
    return round(tasks_completed / tasks_total, 4)


def aggregate(feedback_items: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize feedback dicts containing a rating field."""
    ratings = [float(f.get("rating", 0)) for f in feedback_items if f.get("rating") is not None]
    if not ratings:
        return {"count": 0, "avg_rating": 0.0, "score_pct": 0.0}
    avg = sum(ratings) / len(ratings)
    return {
        "count": len(ratings),
        "avg_rating": round(avg, 2),
        "score_pct": round(avg / 5.0 * 100.0, 2),
    }
