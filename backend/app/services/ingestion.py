"""Parse uploaded Excel/PDF/CSV survey files into structured need records."""
import io
from typing import Any

# Canonical fields we try to populate for each need.
NEED_FIELDS = ("title", "description", "category", "urgency", "location_name", "lat", "lng", "quantity", "unit")

# Common header aliases -> canonical field.
HEADER_ALIASES = {
    "need": "title", "title": "title", "requirement": "title",
    "description": "description", "details": "description", "notes": "description",
    "category": "category", "type": "category", "sector": "category",
    "urgency": "urgency", "priority": "urgency",
    "location": "location_name", "area": "location_name", "place": "location_name",
    "lat": "lat", "latitude": "lat",
    "lng": "lng", "lon": "lng", "long": "lng", "longitude": "lng",
    "quantity": "quantity", "qty": "quantity", "amount": "quantity",
    "unit": "unit", "units": "unit",
}


def _normalize_header(h: str) -> str:
    key = str(h).strip().lower()
    return HEADER_ALIASES.get(key, key)


def _coerce(field: str, value: Any) -> Any:
    if value is None:
        return None
    if field in ("lat", "lng", "quantity"):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    return str(value).strip()


def _row_to_need(row: dict[str, Any]) -> dict[str, Any]:
    need: dict[str, Any] = {}
    for raw_key, raw_val in row.items():
        field = _normalize_header(raw_key)
        if field in NEED_FIELDS:
            need[field] = _coerce(field, raw_val)
    need.setdefault("category", "general")
    need.setdefault("urgency", "medium")
    need.setdefault("title", need.get("description", "Untitled need"))
    return need


def parse_excel(content: bytes) -> list[dict[str, Any]]:
    import pandas as pd  # local import so the module loads without pandas installed

    df = pd.read_excel(io.BytesIO(content))
    return [_row_to_need(r) for r in df.to_dict(orient="records")]


def parse_csv(content: bytes) -> list[dict[str, Any]]:
    import csv

    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    return [_row_to_need(dict(r)) for r in reader]


def parse_pdf(content: bytes) -> list[dict[str, Any]]:
    import pdfplumber  # local import

    needs: list[dict[str, Any]] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if not table or len(table) < 2:
                    continue
                headers = table[0]
                for raw in table[1:]:
                    needs.append(_row_to_need(dict(zip(headers, raw))))
    return needs


def parse_file(filename: str, content: bytes) -> list[dict[str, Any]]:
    """Dispatch on extension. Returns a preview list of need dicts (not persisted)."""
    name = (filename or "").lower()
    if name.endswith((".xlsx", ".xls")):
        return parse_excel(content)
    if name.endswith(".csv"):
        return parse_csv(content)
    if name.endswith(".pdf"):
        return parse_pdf(content)
    raise ValueError(f"Unsupported file type: {filename}")
