from app.services import event_report, events


def _event():
    return {
        "id": "e1",
        "name": "Flood Relief Camp",
        "venue_name": "Town Hall",
        "venue_lat": 17.0,
        "venue_lng": 82.0,
        "radius_km": 5.0,
        "start_at": "2026-01-01T08:00:00",
        "end_at": "2026-01-01T20:00:00",
    }


def test_within_perimeter():
    ev = _event()
    assert events.within_perimeter({"lat": 17.01, "lng": 82.01}, ev) is True
    assert events.within_perimeter({"lat": 40.0, "lng": 10.0}, ev) is False


def test_within_perimeter_missing_coords():
    assert events.within_perimeter({}, _event()) is False


def test_within_window():
    ev = _event()
    assert events.within_window({"created_at": "2026-01-01T10:00:00"}, ev) is True
    assert events.within_window({"created_at": "2026-01-02T10:00:00"}, ev) is False
    assert events.within_window({}, ev) is True  # missing time -> included


def test_filter_for_event():
    ev = _event()
    items = [
        {"lat": 17.0, "lng": 82.0, "created_at": "2026-01-01T10:00:00"},   # in
        {"lat": 17.0, "lng": 82.0, "created_at": "2026-02-01T10:00:00"},   # out of window
        {"lat": 40.0, "lng": 10.0, "created_at": "2026-01-01T10:00:00"},   # out of perimeter
    ]
    assert len(events.filter_for_event(items, ev)) == 1


def test_aggregate_event():
    ev = _event()
    tasks = [
        {"lat": 17.0, "lng": 82.0, "status": "verified", "quantity": 100, "created_at": "2026-01-01T10:00:00"},
        {"lat": 17.0, "lng": 82.0, "status": "accepted", "quantity": 50, "created_at": "2026-01-01T11:00:00"},
        {"lat": 40.0, "lng": 10.0, "status": "verified", "quantity": 999, "created_at": "2026-01-01T10:00:00"},  # outside
    ]
    proofs = [{"lat": 17.0, "lng": 82.0, "created_at": "2026-01-01T10:30:00"}]
    agg = events.aggregate_event(ev, tasks, proofs)
    assert agg["tasks_total"] == 2
    assert agg["tasks_verified"] == 1
    assert agg["tasks_in_progress"] == 1
    assert agg["quantity_delivered"] == 100
    assert agg["proofs_submitted"] == 1
    assert agg["progress_pct"] == 50.0


def test_build_report_data():
    ev = _event()
    tasks = [{"lat": 17.0, "lng": 82.0, "status": "verified", "quantity": 100, "created_at": "2026-01-01T10:00:00"}]
    stories = [{"lat": 17.0, "lng": 82.0, "narrative": "Great work", "task_id": "t1", "created_at": "2026-01-01T12:00:00"}]
    data = event_report.build_report_data(ev, tasks, [], stories)
    assert data["summary"]["tasks_verified"] == 1
    assert data["stories"][0]["narrative"] == "Great work"


def test_render_pdf_returns_bytes():
    ev = _event()
    data = event_report.build_report_data(ev, [], [], [])
    pdf = event_report.render_pdf(data)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 500