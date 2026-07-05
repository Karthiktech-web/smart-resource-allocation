"""Aggregate public-facing platform metrics and NGO trust scores."""
from typing import Any


def platform_scorecards(ngos: list[dict[str, Any]], stories: list[dict[str, Any]], needs: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute headline platform metrics for the landing page."""
    tasks_completed = sum(int(n.get("tasks_completed", 0) or 0) for n in ngos)
    lives_impacted = sum(float(s.get("lives_impacted", 0) or 0) for s in stories)
    needs_resolved = sum(1 for n in needs if n.get("status") in ("verified", "resolved", "completed"))
    verified_stories = sum(1 for s in stories if s.get("verified", True))
    return {
        "ngos_registered": len(ngos),
        "tasks_completed": tasks_completed,
        "lives_impacted": int(lives_impacted),
        "needs_resolved": needs_resolved,
        "verified_stories": verified_stories,
    }


def trust_metrics(ngo: dict[str, Any]) -> dict[str, Any]:
    """Derive an NGO's public trust card."""
    total = int(ngo.get("tasks_total", 0) or 0)
    completed = int(ngo.get("tasks_completed", 0) or 0)
    completion_rate = round(completed / total, 4) if total > 0 else 0.0
    return {
        "id": ngo.get("id"),
        "name": ngo.get("name"),
        "sector": ngo.get("sector"),
        "regions": ngo.get("regions", []),
        "reliability_score": round(float(ngo.get("reliability_score", 0.0) or 0.0), 2),
        "tasks_total": total,
        "tasks_completed": completed,
        "completion_rate": completion_rate,
        "verified": bool(ngo.get("verified", False)),
    }


def rank_directory(ngos: list[dict[str, Any]], sector: str | None = None, search: str | None = None) -> list[dict[str, Any]]:
    """Filter + sort NGOs for the public directory (most trustworthy first)."""
    cards = [trust_metrics(n) for n in ngos]
    if sector:
        cards = [c for c in cards if (c["sector"] or "").lower() == sector.lower()]
    if search:
        q = search.lower()
        cards = [c for c in cards if q in (c["name"] or "").lower()]
    return sorted(
        cards,
        key=lambda c: (c["verified"], c["reliability_score"], c["tasks_completed"]),
        reverse=True,
    )