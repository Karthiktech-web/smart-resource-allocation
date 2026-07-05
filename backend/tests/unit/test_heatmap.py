from app.services import heatmap


def _needs():
    return [
        {
            "area_id": "A",
            "category": "water",
            "quantity": 100,
            "lat": 17.0,
            "lng": 82.0,
            "created_at": "2025-05-01T00:00:00",
        },
        {
            "area_id": "A",
            "category": "water",
            "quantity": 200,
            "lat": 17.0,
            "lng": 82.0,
            "created_at": "2025-05-02T00:00:00",
        },
        {
            "area_id": "B",
            "category": "water",
            "quantity": 50,
            "lat": 18.0,
            "lng": 83.0,
            "created_at": "2025-05-01T00:00:00",
        },
    ]


def test_aggregate_by_area():
    agg = heatmap.aggregate_by_area(_needs())
    assert agg["A"]["count"] == 2
    assert agg["A"]["total_quantity"] == 300


def test_forecast_ranks_hotter_zone_first():
    zones = heatmap.forecast(_needs(), target_month=5, category="water")
    assert zones[0]["area_id"] == "A"
    assert zones[0]["predicted_intensity"] == 285.0


def test_forecast_seasonal_effect():
    hot = heatmap.forecast(_needs(), 5, "water")[0]["predicted_intensity"]
    cold = heatmap.forecast(_needs(), 1, "water")[0]["predicted_intensity"]
    assert hot > cold
