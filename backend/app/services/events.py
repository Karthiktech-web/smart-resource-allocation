"""Event & Emergency mode: venue-centric filtering + live aggregation + PDF summary."""
from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from typing import Any

EARTH_RADIUS_KM = 6371.0


def haversine_km(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    dlat = radians(b_lat - a_lat)
    dlng = radians(b_lng - a_lng)
    h = sin(dlat / 2) ** 2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(h))


def within_perimeter(item: dict[str, Any], event: dict[str, Any]) -> bool:
    """True if item's coords fall inside the event's venue radius."""
    lat, lng = item.get("lat"), item.get("lng")
    if lat is None or lng is None:
        return False
    radius = float(event.get("radius_km", 5.0) or 5.0)
    dist = haversine_km(
        float(event["venue_lat"]), float(event["venue_lng"]), float(lat), float(lng)
    )
    return dist <= radius


def _parse(iso: str | None) -> datetime | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None


def within_window(item: dict[str, Any], event: dict[str, Any]) -> bool:
    """True if item's created_at falls within the event's start/end window.

    Missing event bounds are treated as open-ended; missing item time -> included.
    """
    t = _parse(item.get("created_at"))
    if t is None:
        return True
    start, end = _parse(event.get("start_at")), _parse(event.get("end_at"))
    if start and t < start:
        return False
    if end and t > end:
        return False
    return True


def filter_for_event(items: list[dict[str, Any]], event: dict[str, Any]) -> list[dict[str, Any]]:
    """Keep only items inside the venue perimeter AND the event time window."""
    return [i for i in items if within_perimeter(i, event) and within_window(i, event)]


def aggregate_event(event: dict[str, Any], tasks: list[dict[str, Any]], proofs: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute live-tracker metrics for an event from its in-perimeter tasks/proofs."""
    ev_tasks = filter_for_event(tasks, event)
    ev_proofs = filter_for_event(proofs, event)

    total = len(ev_tasks)
    verified = sum(1 for t in ev_tasks if t.get("status") == "verified")
    in_progress = sum(1 for t in ev_tasks if t.get("status") in ("accepted", "acted", "broadcast"))
    delivered = sum(float(t.get("quantity", 0) or 0) for t in ev_tasks if t.get("status") == "verified")
    progress_pct = round(100.0 * verified / total, 1) if total else 0.0

    return {
        "event_id": event.get("id"),
        "name": event.get("name"),
        "tasks_total": total,
        "tasks_verified": verified,
        "tasks_in_progress": in_progress,
        "quantity_delivered": round(delivered, 2),
        "proofs_submitted": len(ev_proofs),
        "progress_pct": progress_pct,
    }