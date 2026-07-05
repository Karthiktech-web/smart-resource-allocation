"""Matching engine: rank NGOs for a task by proximity, capacity, and reliability."""
from math import asin, cos, radians, sin, sqrt
from typing import Any

EARTH_RADIUS_KM = 6371.0
DEFAULT_WEIGHTS = (0.4, 0.3, 0.3)  # proximity, capacity, reliability


def haversine(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    """Great-circle distance between two points in kilometers."""
    dlat = radians(b_lat - a_lat)
    dlng = radians(b_lng - a_lng)
    h = (
        sin(dlat / 2) ** 2
        + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlng / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * asin(sqrt(h))


def score(ngo: dict[str, Any], task: dict[str, Any], weights=DEFAULT_WEIGHTS) -> float:
    """Return a 0..1-ish match score for an NGO against a task."""
    dist = haversine(
        task.get("lat", 0.0),
        task.get("lng", 0.0),
        ngo.get("lat", 0.0),
        ngo.get("lng", 0.0),
    )
    proximity = 1.0 / (1.0 + dist)

    max_concurrent = max(1, int(ngo.get("max_concurrent", 5)))
    active = int(ngo.get("active_assignments", 0))
    capacity = max(0, max_concurrent - active) / max_concurrent

    reliability = float(ngo.get("reliability_score", 0.0)) / 100.0

    w1, w2, w3 = weights
    return w1 * proximity + w2 * capacity + w3 * reliability


def reasoning(ngo: dict[str, Any], task: dict[str, Any]) -> str:
    dist = haversine(
        task.get("lat", 0.0), task.get("lng", 0.0),
        ngo.get("lat", 0.0), ngo.get("lng", 0.0),
    )
    free = max(0, int(ngo.get("max_concurrent", 5)) - int(ngo.get("active_assignments", 0)))
    return (
        f"{ngo.get('name', 'NGO')} is {dist:.1f} km away, has {free} free slots, "
        f"and a reliability score of {float(ngo.get('reliability_score', 0)):.0f}."
    )


def rank(ngos: list[dict[str, Any]], task: dict[str, Any], weights=DEFAULT_WEIGHTS):
    """Return NGOs sorted best-first, each annotated with score + reasoning."""
    scored = [
        {**ngo, "match_score": round(score(ngo, task, weights), 4), "reasoning": reasoning(ngo, task)}
        for ngo in ngos
    ]
    return sorted(scored, key=lambda n: n["match_score"], reverse=True)
