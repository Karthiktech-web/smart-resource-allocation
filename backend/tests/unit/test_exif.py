from datetime import datetime, timezone

from app.services import exif


def test_dms_to_deg_and_extract_gps():
    gps = {1: "N", 2: ((17, 1), (0, 1), (0, 1)), 3: "E", 4: ((82, 1), (0, 1), (0, 1))}
    lat, lng = exif.extract_gps(gps)
    assert abs(lat - 17.0) < 1e-6
    assert abs(lng - 82.0) < 1e-6


def test_extract_gps_southern_western_hemisphere():
    gps = {1: "S", 2: ((10, 1), (30, 1), (0, 1)), 3: "W", 4: ((20, 1), (0, 1), (0, 1))}
    lat, lng = exif.extract_gps(gps)
    assert lat < 0 and lng < 0
    assert abs(lat - -10.5) < 1e-6


def test_extract_gps_missing_returns_none():
    assert exif.extract_gps({}) is None


def test_parse_datetime():
    dt = exif.parse_datetime("2026:01:02 09:30:00")
    assert dt == datetime(2026, 1, 2, 9, 30, tzinfo=timezone.utc)
    assert exif.parse_datetime("garbage") is None


def test_validate_pass():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    res = exif.validate((17.0, 82.0), now, 17.001, 82.001, now)
    assert res["valid"] is True
    assert res["location_ok"] and res["time_ok"]


def test_validate_far_location_fails():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    res = exif.validate((0.0, 0.0), now, 17.0, 82.0, now)
    assert res["valid"] is False
    assert res["location_ok"] is False
    assert "km" in res["reason"]


def test_validate_no_gps_flagged():
    res = exif.validate(None, None, 17.0, 82.0, None)
    assert res["valid"] is False
    assert res["has_gps"] is False
