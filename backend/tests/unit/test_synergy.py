from app.services import synergy


def test_haversine_km():
    assert synergy.haversine_km(0, 0, 0, 0) == 0
    assert 110 < synergy.haversine_km(0, 0, 1, 0) < 112


def test_find_synergies_pairs_nearby_time_aligned():
    trips = [
        {"ngo_id": "a", "dest_lat": 17.0, "dest_lng": 82.0, "depart_at": "2026-01-01T09:00:00"},
        {"ngo_id": "b", "dest_lat": 17.01, "dest_lng": 82.01, "depart_at": "2026-01-01T09:30:00"},
        {"ngo_id": "c", "dest_lat": 40.0, "dest_lng": 10.0, "depart_at": "2026-01-01T09:00:00"},
    ]
    out = synergy.find_synergies(trips)
    assert len(out) == 1
    assert {out[0]["ngo_a"], out[0]["ngo_b"]} == {"a", "b"}


def test_find_synergies_excludes_far_in_time():
    trips = [
        {"ngo_id": "a", "dest_lat": 17.0, "dest_lng": 82.0, "depart_at": "2026-01-01T09:00:00"},
        {"ngo_id": "b", "dest_lat": 17.01, "dest_lng": 82.01, "depart_at": "2026-01-01T20:00:00"},
    ]
    assert synergy.find_synergies(trips) == []


def test_find_synergies_ignores_same_ngo():
    trips = [
        {"ngo_id": "a", "dest_lat": 17.0, "dest_lng": 82.0, "depart_at": "2026-01-01T09:00:00"},
        {"ngo_id": "a", "dest_lat": 17.0, "dest_lng": 82.0, "depart_at": "2026-01-01T09:10:00"},
    ]
    assert synergy.find_synergies(trips) == []
