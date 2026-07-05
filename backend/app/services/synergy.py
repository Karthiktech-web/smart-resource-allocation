"""Logistics synergy: suggest NGOs sharing transport when routes overlap."""
from datetime import datetime
from itertools import combinations
from math import asin, cos, radians, sin, sqrt
from typing import Any

EARTH_RADIUS_KM = 6371.0


def haversine_km(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    dlat = radians(b_lat - a_lat)
    dlng = radians(b_lng - a_lng)
    h = sin(dlat / 2) ** 2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(h))


def _parse(iso: str | None) -> datetime | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        return None


def find_synergies(
    trips: list[dict[str, Any]],
    *,
    proximity_km: float = 5.0,
    time_window_hours: float = 2.0,
) -> list[dict[str, Any]]:
    """Pair trips whose destinations are near each other and depart around the same time."""
    suggestions = []
    for a, b in combinations(trips, 2):
        if a.get("ngo_id") == b.get("ngo_id"):
            continue

        dist = haversine_km(
            float(a.get("dest_lat", 0)),
            float(a.get("dest_lng", 0)),
            float(b.get("dest_lat", 0)),
            float(b.get("dest_lng", 0)),
        )
        if dist > proximity_km:
            continue

        ta, tb = _parse(a.get("depart_at")), _parse(b.get("depart_at"))
        gap_hours = None
        if ta and tb:
            gap_hours = abs((ta - tb).total_seconds()) / 3600.0
            if gap_hours > time_window_hours:
                continue

        suggestions.append(
            {
                "ngo_a": a.get("ngo_id"),
                "ngo_b": b.get("ngo_id"),
                "distance_km": round(dist, 2),
                "time_gap_hours": round(gap_hours, 2) if gap_hours is not None else None,
                "message": (
                    f"{a.get('ngo_id')} and {b.get('ngo_id')} are heading {dist:.1f} km apart"
                    + (f" within {gap_hours:.1f}h" if gap_hours is not None else "")
                    + " - consider sharing transport."
                ),
            }
        )
    return sorted(suggestions, key=lambda s: s["distance_km"])
