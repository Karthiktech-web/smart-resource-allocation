"""Extract and validate GPS/timestamp EXIF metadata from proof-of-work photos."""
from datetime import datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt
from typing import Any

EARTH_RADIUS_KM = 6371.0


def _haversine_km(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    dlat = radians(b_lat - a_lat)
    dlng = radians(b_lng - a_lng)
    h = sin(dlat / 2) ** 2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(h))


def _dms_to_deg(dms, ref: str) -> float:
    """Convert EXIF degrees/minutes/seconds rationals to signed decimal degrees."""

    def _r(x):
        return x[0] / x[1] if isinstance(x, (tuple, list)) else float(x)

    deg = _r(dms[0]) + _r(dms[1]) / 60.0 + _r(dms[2]) / 3600.0
    if ref in ("S", "W"):
        deg = -deg
    return deg


def extract_gps(exif_gps: dict[Any, Any]) -> tuple[float, float] | None:
    """Return (lat, lng) from a piexif GPS IFD dict, or None if absent."""
    if not exif_gps:
        return None
    try:
        lat_ref = exif_gps[1].decode() if isinstance(exif_gps[1], bytes) else exif_gps[1]
        lng_ref = exif_gps[3].decode() if isinstance(exif_gps[3], bytes) else exif_gps[3]
        lat = _dms_to_deg(exif_gps[2], lat_ref)
        lng = _dms_to_deg(exif_gps[4], lng_ref)
        return (lat, lng)
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def parse_datetime(dt_str: str | None) -> datetime | None:
    """Parse an EXIF DateTimeOriginal string ('YYYY:MM:DD HH:MM:SS')."""
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def validate(
    photo_gps: tuple[float, float] | None,
    photo_time: datetime | None,
    expected_lat: float,
    expected_lng: float,
    expected_time: datetime | None,
    *,
    radius_km: float = 2.0,
    window_hours: float = 24.0,
) -> dict[str, Any]:
    """Validate photo location/time against the task's expected location/time."""
    result: dict[str, Any] = {
        "has_gps": photo_gps is not None,
        "has_timestamp": photo_time is not None,
        "distance_km": None,
        "location_ok": False,
        "time_ok": False,
        "valid": False,
        "reason": "",
    }

    if photo_gps is not None:
        dist = _haversine_km(photo_gps[0], photo_gps[1], expected_lat, expected_lng)
        result["distance_km"] = round(dist, 3)
        result["location_ok"] = dist <= radius_km

    if photo_time is not None and expected_time is not None:
        result["time_ok"] = abs(photo_time - expected_time) <= timedelta(hours=window_hours)
    elif photo_time is not None and expected_time is None:
        result["time_ok"] = True

    result["valid"] = result["location_ok"] and result["time_ok"]
    if not result["has_gps"]:
        result["reason"] = "Photo has no GPS metadata"
    elif not result["location_ok"]:
        result["reason"] = f"Photo taken {result['distance_km']} km from task location (> {radius_km} km)"
    elif not result["time_ok"]:
        result["reason"] = "Photo timestamp outside allowed window"
    else:
        result["reason"] = "Location and time verified"
    return result


def extract_from_bytes(image_bytes: bytes) -> dict[str, Any]:
    """Extract gps + datetime from raw image bytes using piexif."""
    import piexif

    exif = piexif.load(image_bytes)
    gps = extract_gps(exif.get("GPS", {}))
    dt_raw = exif.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)
    if isinstance(dt_raw, bytes):
        dt_raw = dt_raw.decode(errors="replace")
    return {"gps": gps, "taken_at": parse_datetime(dt_raw)}
