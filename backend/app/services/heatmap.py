"""Predictive heatmapping from historical needs."""
from collections import defaultdict
from typing import Any

SEASONAL_WATER = {
    1: 0.8,
    2: 0.9,
    3: 1.2,
    4: 1.6,
    5: 1.9,
    6: 1.7,
    7: 1.0,
    8: 0.9,
    9: 0.9,
    10: 1.0,
    11: 0.9,
    12: 0.8,
}


def _month_of(iso: str | None) -> int | None:
    if not iso or len(iso) < 7:
        return None
    try:
        return int(iso[5:7])
    except ValueError:
        return None


def aggregate_by_area(needs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Group historical needs by area_id, summing quantities and counting records."""
    agg: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"count": 0, "total_quantity": 0.0, "lat": 0.0, "lng": 0.0}
    )
    for need in needs:
        area = need.get("area_id") or need.get("location_name") or "unknown"
        area_data = agg[area]
        area_data["count"] += 1
        area_data["total_quantity"] += float(need.get("quantity", 0) or 0)
        area_data["lat"] = float(need.get("lat", area_data["lat"]) or area_data["lat"])
        area_data["lng"] = float(need.get("lng", area_data["lng"]) or area_data["lng"])
    return dict(agg)


def forecast(needs: list[dict[str, Any]], target_month: int, category: str = "water") -> list[dict[str, Any]]:
    """Produce a ranked list of predicted hot zones for the target month."""
    seasonal = SEASONAL_WATER.get(target_month, 1.0) if category == "water" else 1.0
    relevant = [n for n in needs if category in (n.get("category", ""), "any") or category == "any"]
    agg = aggregate_by_area(relevant or needs)

    zones = []
    for area, area_data in agg.items():
        avg_qty = area_data["total_quantity"] / area_data["count"] if area_data["count"] else 0.0
        intensity = round(avg_qty * seasonal, 2)
        zones.append(
            {
                "area_id": area,
                "lat": area_data["lat"],
                "lng": area_data["lng"],
                "historical_count": area_data["count"],
                "avg_quantity": round(avg_qty, 2),
                "seasonal_multiplier": seasonal,
                "predicted_intensity": intensity,
            }
        )
    return sorted(zones, key=lambda z: z["predicted_intensity"], reverse=True)
