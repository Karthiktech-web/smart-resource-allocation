"""Split a large task into subtasks sized to available NGO capacity."""
from typing import Any


def split_quantity(total: float, capacities: list[float]) -> list[float]:
    """Greedily allocate `total` across the given per-NGO capacities.

    Returns the chunk assigned to each NGO (same order as `capacities`).
    Any remainder that cannot be covered is dropped from the result.

    Example: split_quantity(1700, [900, 600, 400]) -> [900, 600, 200]
    """
    remaining = total
    chunks: list[float] = []
    for cap in capacities:
        if remaining <= 0:
            break
        take = min(cap, remaining)
        if take > 0:
            chunks.append(take)
            remaining -= take
    return chunks


def build_subtasks(task: dict[str, Any], ranked_ngos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create subtask dicts for a task given ranked NGOs with `capacity_units`.

    Each NGO's capacity comes from `capacity_units` (fallback: free assignment
    slots). If the task quantity fits one NGO, a single subtask is returned.
    """
    total = float(task.get("quantity", 0) or 0)
    caps = [
        float(n.get("capacity_units", max(0, int(n.get("max_concurrent", 5)) - int(n.get("active_assignments", 0)))))
        for n in ranked_ngos
    ]
    chunks = split_quantity(total, caps) if total > 0 else []

    subtasks: list[dict[str, Any]] = []
    for ngo, chunk in zip(ranked_ngos, chunks):
        subtasks.append(
            {
                "need_id": task.get("need_id"),
                "title": task.get("title"),
                "category": task.get("category"),
                "unit": task.get("unit", ""),
                "area_id": task.get("area_id"),
                "lat": task.get("lat", 0),
                "lng": task.get("lng", 0),
                "quantity": chunk,
                "parent_task_id": task.get("id"),
                "assigned_ngo_id": ngo.get("id"),
                "status": "broadcast",
            }
        )
    return subtasks
