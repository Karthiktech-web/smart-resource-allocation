from app.services import anomaly


def test_zscore_outliers():
    vals = [10, 11, 9, 10, 500]
    assert anomaly.zscore_outliers(vals) == [4]


def test_zscore_needs_min_three():
    assert anomaly.zscore_outliers([1, 100]) == []


def test_rate_anomaly_water():
    assert anomaly.rate_anomaly(100000, 1, "water") is True
    assert anomaly.rate_anomaly(50, 1, "water") is False


def test_rate_anomaly_zero_minutes():
    assert anomaly.rate_anomaly(10, 0, "water") is True


def test_scan_submission_flags_rate():
    verdict = anomaly.scan_submission({"quantity": 100000, "duration_minutes": 1, "category": "water"}, [])
    assert verdict["flagged"] is True
    assert any("rate" in reason.lower() for reason in verdict["reasons"])


def test_scan_submission_negative():
    verdict = anomaly.scan_submission({"quantity": -5, "duration_minutes": 10, "category": "food"}, [])
    assert verdict["flagged"] is True


def test_scan_batch_marks_outlier():
    submissions = [
        {"quantity": 10, "category": "food", "duration_minutes": 60},
        {"quantity": 11, "category": "food", "duration_minutes": 60},
        {"quantity": 9, "category": "food", "duration_minutes": 60},
        {"quantity": 9000, "category": "food", "duration_minutes": 6000},
    ]
    results = anomaly.scan_batch(submissions)
    assert results[-1]["flagged"] is True
