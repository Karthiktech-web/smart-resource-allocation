"""Detect stagnant assignments and re-queue their tasks to the next-best NGO."""
from datetime import datetime, timezone
from typing import Any


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def is_stagnant(assignment: dict[str, Any], sla_minutes: int, now: datetime | None = None) -> bool:
    """True if the assignment was accepted but not acted on within the SLA."""
    if assignment.get("status") != "accepted":
        return False
    if assignment.get("acted_at"):
        return False
    accepted = _parse_iso(assignment.get("accepted_at"))
    if accepted is None:
        return False
    now = now or datetime.now(timezone.utc)
    if accepted.tzinfo is None:
        accepted = accepted.replace(tzinfo=timezone.utc)
    elapsed_minutes = (now - accepted).total_seconds() / 60.0
    return elapsed_minutes > sla_minutes


def find_stagnant(assignments: list[dict[str, Any]], sla_minutes: int, now: datetime | None = None):
    return [a for a in assignments if is_stagnant(a, sla_minutes, now)]
