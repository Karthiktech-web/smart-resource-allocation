from app.services import matching


def test_haversine_zero_distance():
    assert matching.haversine(0, 0, 0, 0) == 0


def test_haversine_known_distance():
    d = matching.haversine(0, 0, 1, 0)
    assert 110 < d < 112


def test_score_prefers_closer_higher_capacity_reliable():
    task = {"lat": 0.0, "lng": 0.0}
    near = {"lat": 0.1, "lng": 0.1, "max_concurrent": 5, "active_assignments": 0, "reliability_score": 90}
    far = {"lat": 5.0, "lng": 5.0, "max_concurrent": 5, "active_assignments": 4, "reliability_score": 10}
    assert matching.score(near, task) > matching.score(far, task)


def test_rank_orders_best_first_and_annotates():
    task = {"lat": 0.0, "lng": 0.0}
    ngos = [
        {"id": "far", "name": "Far", "lat": 10, "lng": 10, "max_concurrent": 5, "active_assignments": 5, "reliability_score": 0},
        {"id": "near", "name": "Near", "lat": 0.1, "lng": 0.1, "max_concurrent": 5, "active_assignments": 0, "reliability_score": 100},
    ]
    ranked = matching.rank(ngos, task)
    assert ranked[0]["id"] == "near"
    assert "match_score" in ranked[0] and "reasoning" in ranked[0]
