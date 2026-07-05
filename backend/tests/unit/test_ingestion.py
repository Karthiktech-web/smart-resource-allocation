from app.services import ingestion


def test_parse_csv_maps_aliases():
    csv_bytes = b"Need,Category,Priority,Area,Quantity,Unit\nClean water,water,critical,Rampur,1700,L\n"
    needs = ingestion.parse_csv(csv_bytes)
    assert len(needs) == 1
    n = needs[0]
    assert n["title"] == "Clean water"
    assert n["category"] == "water"
    assert n["urgency"] == "critical"
    assert n["location_name"] == "Rampur"
    assert n["quantity"] == 1700.0
    assert n["unit"] == "L"


def test_parse_csv_defaults():
    needs = ingestion.parse_csv(b"description\nSome need without category\n")
    assert needs[0]["category"] == "general"
    assert needs[0]["urgency"] == "medium"
    assert needs[0]["title"] == "Some need without category"


def test_parse_file_rejects_unknown():
    try:
        ingestion.parse_file("data.txt", b"x")
        assert False, "expected ValueError"
    except ValueError:
        pass
