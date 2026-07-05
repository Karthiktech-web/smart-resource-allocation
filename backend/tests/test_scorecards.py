from app.services import scorecards


def _ngos():
    return [
        {"id": "a", "name": "Alpha", "sector": "water", "reliability_score": 90, "tasks_total": 10, "tasks_completed": 9, "verified": True},
        {"id": "b", "name": "Beta", "sector": "food", "reliability_score": 70, "tasks_total": 10, "tasks_completed": 5, "verified": True},
        {"id": "c", "name": "Gamma", "sector": "water", "reliability_score": 99, "tasks_total": 4, "tasks_completed": 4, "verified": False},
    ]


def test_platform_scorecards():
    m = scorecards.platform_scorecards(
        _ngos(),
        [{"lives_impacted": 100}, {"lives_impacted": 50}],
        [{"status": "verified"}, {"status": "open"}, {"status": "resolved"}],
    )
    assert m["ngos_registered"] == 3
    assert m["tasks_completed"] == 18
    assert m["lives_impacted"] == 150
    assert m["needs_resolved"] == 2


def test_trust_metrics_completion_rate():
    card = scorecards.trust_metrics(_ngos()[0])
    assert card["completion_rate"] == 0.9


def test_trust_metrics_zero_total():
    card = scorecards.trust_metrics({"id": "x", "tasks_total": 0, "tasks_completed": 0})
    assert card["completion_rate"] == 0.0


def test_rank_directory_verified_first():
    ranked = scorecards.rank_directory(_ngos())
    assert [c["id"] for c in ranked] == ["a", "b", "c"]


def test_rank_directory_sector_filter():
    ranked = scorecards.rank_directory(_ngos(), sector="water")
    assert {c["id"] for c in ranked} == {"a", "c"}


def test_rank_directory_search():
    ranked = scorecards.rank_directory(_ngos(), search="alp")
    assert [c["id"] for c in ranked] == ["a"]