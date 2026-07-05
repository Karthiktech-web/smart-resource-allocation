from app.services import task_splitter


def test_split_quantity_basic():
    assert task_splitter.split_quantity(1700, [900, 600, 400]) == [900, 600, 200]


def test_split_quantity_fits_single():
    assert task_splitter.split_quantity(300, [900]) == [300]


def test_split_quantity_insufficient_capacity_drops_remainder():
    assert task_splitter.split_quantity(1000, [300, 200]) == [300, 200]


def test_build_subtasks_splits_across_ngos():
    task = {"id": "t1", "need_id": "n1", "title": "Water", "category": "water", "quantity": 1300, "unit": "L", "lat": 0, "lng": 0}
    ngos = [{"id": "a", "capacity_units": 900}, {"id": "b", "capacity_units": 900}]
    subs = task_splitter.build_subtasks(task, ngos)
    assert [s["quantity"] for s in subs] == [900, 400]
    assert all(s["parent_task_id"] == "t1" for s in subs)
    assert subs[0]["assigned_ngo_id"] == "a"


def test_build_subtasks_single_ngo_when_fits():
    task = {"id": "t1", "need_id": "n1", "title": "Food", "category": "food", "quantity": 200, "unit": "kg", "lat": 0, "lng": 0}
    ngos = [{"id": "a", "capacity_units": 900}]
    subs = task_splitter.build_subtasks(task, ngos)
    assert len(subs) == 1 and subs[0]["quantity"] == 200
