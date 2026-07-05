from datetime import datetime, timedelta, timezone

from app.services import requeue


def _now():
    return datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def test_stagnant_when_idle_past_sla():
    a = {"status": "accepted", "accepted_at": (_now() - timedelta(minutes=200)).isoformat(), "acted_at": None}
    assert requeue.is_stagnant(a, sla_minutes=120, now=_now()) is True


def test_not_stagnant_when_recent():
    a = {"status": "accepted", "accepted_at": (_now() - timedelta(minutes=10)).isoformat(), "acted_at": None}
    assert requeue.is_stagnant(a, sla_minutes=120, now=_now()) is False


def test_not_stagnant_when_acted():
    a = {"status": "accepted", "accepted_at": (_now() - timedelta(minutes=200)).isoformat(), "acted_at": _now().isoformat()}
    assert requeue.is_stagnant(a, sla_minutes=120, now=_now()) is False


def test_find_stagnant_filters():
    items = [
        {"id": "1", "task_id": "t1", "status": "accepted", "accepted_at": (_now() - timedelta(minutes=200)).isoformat(), "acted_at": None},
        {"id": "2", "task_id": "t2", "status": "accepted", "accepted_at": (_now() - timedelta(minutes=5)).isoformat(), "acted_at": None},
    ]
    result = requeue.find_stagnant(items, sla_minutes=120, now=_now())
    assert [r["id"] for r in result] == ["1"]
