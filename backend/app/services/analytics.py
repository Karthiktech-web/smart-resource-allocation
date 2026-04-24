from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from app.database import get_db


def _read_collection(name: str) -> list[dict[str, Any]]:
    db = get_db()
    items: list[dict[str, Any]] = []
    for doc in db.collection(name).stream():
        item = doc.to_dict() or {}
        item["id"] = doc.id
        items.append(item)
    return items


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            normalized = value.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _within_days(value: Any, days: int) -> bool:
    parsed = _parse_datetime(value)
    if parsed is None:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return parsed >= cutoff


def _round(value: float) -> float:
    return round(value, 1)


async def get_trends(days: int = 30) -> dict[str, Any]:
    needs = _read_collection("needs")
    impact_logs = _read_collection("impact_logs")

    needs_by_day: dict[str, int] = defaultdict(int)
    resolved_by_day: dict[str, int] = defaultdict(int)
    needs_by_category: dict[str, int] = defaultdict(int)
    urgency_distribution: dict[str, int] = defaultdict(int)
    impact_by_day: dict[str, dict[str, float]] = defaultdict(
        lambda: {"people_helped": 0, "volunteer_hours": 0.0}
    )

    for need in needs:
        created = _parse_datetime(need.get("created_at"))
        if created and _within_days(created, days):
            day_key = created.astimezone(timezone.utc).strftime("%Y-%m-%d")
            needs_by_day[day_key] += 1
            needs_by_category[need.get("category", "other")] += 1
            urgency_distribution[need.get("urgency", "low")] += 1

        updated = _parse_datetime(need.get("updated_at"))
        if need.get("status") == "resolved" and updated and _within_days(updated, days):
            resolved_day = updated.astimezone(timezone.utc).strftime("%Y-%m-%d")
            resolved_by_day[resolved_day] += 1

    for log in impact_logs:
        created = _parse_datetime(log.get("created_at"))
        if created and _within_days(created, days):
            day_key = created.astimezone(timezone.utc).strftime("%Y-%m-%d")
            impact_by_day[day_key]["people_helped"] += int(log.get("people_helped", 0) or 0)
            impact_by_day[day_key]["volunteer_hours"] += float(log.get("volunteer_hours", 0) or 0)

    all_days = sorted(set(needs_by_day.keys()) | set(resolved_by_day.keys()))

    return {
        "time_range_days": days,
        "needs_timeline": [
            {
                "date": day,
                "needs_created": needs_by_day.get(day, 0),
                "needs_resolved": resolved_by_day.get(day, 0),
            }
            for day in all_days
        ],
        "needs_by_category": dict(sorted(needs_by_category.items())),
        "urgency_distribution": dict(sorted(urgency_distribution.items())),
        "impact_timeline": [
            {
                "date": day,
                "people_helped": int(values["people_helped"]),
                "volunteer_hours": _round(values["volunteer_hours"]),
            }
            for day, values in sorted(impact_by_day.items())
        ],
        "summary": {
            "total_needs_period": sum(needs_by_day.values()),
            "total_resolved_period": sum(resolved_by_day.values()),
            "total_people_helped": int(sum(values["people_helped"] for values in impact_by_day.values())),
            "total_volunteer_hours": _round(sum(values["volunteer_hours"] for values in impact_by_day.values())),
            "avg_needs_per_day": _round(sum(needs_by_day.values()) / max(len(needs_by_day), 1)),
            "avg_resolutions_per_day": _round(sum(resolved_by_day.values()) / max(len(resolved_by_day), 1)),
        },
    }


async def get_efficiency_metrics() -> dict[str, Any]:
    areas = _read_collection("areas")
    all_needs = _read_collection("needs")
    volunteers = _read_collection("volunteers")

    total_needs = len(all_needs)
    resolved_needs = len([need for need in all_needs if need.get("status") == "resolved"])
    assigned_needs = len(
        [need for need in all_needs if need.get("status") in {"assigned", "in_progress"}]
    )
    open_needs = len([need for need in all_needs if need.get("status") == "open"])

    total_volunteers = len(volunteers)
    active_volunteers = len(
        [volunteer for volunteer in volunteers if int(volunteer.get("active_assignments", 0) or 0) > 0]
    )
    total_capacity = sum(int(volunteer.get("max_concurrent_assignments", 3) or 3) for volunteer in volunteers)
    used_capacity = sum(int(volunteer.get("active_assignments", 0) or 0) for volunteer in volunteers)

    total_volunteer_gap = sum(int(area.get("volunteer_gap", 0) or 0) for area in areas)
    total_recommended = sum(int(area.get("volunteers_recommended", 0) or 0) for area in areas)
    total_assigned_to_areas = sum(int(area.get("volunteers_assigned", 0) or 0) for area in areas)

    avg_reliability = (
        sum(float(volunteer.get("reliability_score", 0) or 0) for volunteer in volunteers)
        / max(total_volunteers, 1)
    )
    resolution_rate = (resolved_needs / max(total_needs, 1)) * 100
    areas_fully_covered = len([area for area in areas if int(area.get("volunteer_gap", 0) or 0) <= 0])
    coverage_rate = (areas_fully_covered / max(len(areas), 1)) * 100
    utilization_rate = (used_capacity / max(total_capacity, 1)) * 100

    return {
        "needs_metrics": {
            "total": total_needs,
            "open": open_needs,
            "assigned": assigned_needs,
            "resolved": resolved_needs,
            "resolution_rate": _round(resolution_rate),
            "assignment_rate": _round((assigned_needs / max(total_needs, 1)) * 100),
        },
        "volunteer_metrics": {
            "total": total_volunteers,
            "active": active_volunteers,
            "idle": total_volunteers - active_volunteers,
            "utilization_rate": _round(utilization_rate),
            "avg_reliability": round(avg_reliability, 2),
            "total_capacity": total_capacity,
            "used_capacity": used_capacity,
        },
        "area_metrics": {
            "total_areas": len(areas),
            "fully_covered": areas_fully_covered,
            "coverage_rate": _round(coverage_rate),
            "total_volunteer_gap": total_volunteer_gap,
            "critical_areas": len([area for area in areas if area.get("area_priority") == "critical"]),
            "high_priority_areas": len([area for area in areas if area.get("area_priority") == "high"]),
        },
        "allocation_efficiency": {
            "volunteers_recommended": total_recommended,
            "volunteers_assigned": total_assigned_to_areas,
            "fill_rate": _round((total_assigned_to_areas / max(total_recommended, 1)) * 100),
            "overall_efficiency_score": _round(
                (
                    resolution_rate * 0.3
                    + coverage_rate * 0.3
                    + utilization_rate * 0.2
                    + avg_reliability * 100 * 0.2
                )
            ),
        },
    }
