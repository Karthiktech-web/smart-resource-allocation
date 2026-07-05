from app.services import reliability


def test_update_score_moves_toward_rating():
    new = reliability.update_score(50.0, 5.0, tasks_completed=0)
    assert new > 50.0


def test_update_score_low_rating_drops():
    new = reliability.update_score(80.0, 1.0, tasks_completed=0)
    assert new < 80.0


def test_update_score_more_tasks_more_inertia():
    fresh = reliability.update_score(50.0, 5.0, tasks_completed=0)
    seasoned = reliability.update_score(50.0, 5.0, tasks_completed=20)
    assert (fresh - 50.0) > (seasoned - 50.0)


def test_completion_rate():
    assert reliability.completion_rate(3, 4) == 0.75
    assert reliability.completion_rate(0, 0) == 0.0


def test_aggregate():
    agg = reliability.aggregate([{"rating": 5}, {"rating": 3}])
    assert agg["count"] == 2
    assert agg["avg_rating"] == 4.0
    assert agg["score_pct"] == 80.0


def test_aggregate_empty():
    agg = reliability.aggregate([])
    assert agg == {"count": 0, "avg_rating": 0.0, "score_pct": 0.0}
