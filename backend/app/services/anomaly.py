"""Statistical anomaly detection for report/proof submissions."""
from statistics import median
from typing import Any

Z_THRESHOLD = 3.5

MAX_RATE_PER_MINUTE = {
    "water": 100.0,
    "food": 50.0,
    "default": 1000.0,
}


def _modified_zscores(values: list[float]) -> list[float]:
    """Robust modified z-scores using median and MAD."""
    med = median(values)
    abs_dev = [abs(v - med) for v in values]
    mad = median(abs_dev)
    if mad == 0:
        return [0.0 for _ in values]
    return [0.6745 * (v - med) / mad for v in values]


def zscore_outliers(values: list[float], threshold: float = Z_THRESHOLD) -> list[int]:
    """Return indices whose robust modified z-score exceeds the threshold."""
    if len(values) < 3:
        return []
    scores = _modified_zscores(values)
    return [i for i, z in enumerate(scores) if abs(z) > threshold]


def rate_anomaly(quantity: float, minutes: float, category: str) -> bool:
    """True if delivering quantity in minutes exceeds a plausible rate."""
    if minutes <= 0:
        return quantity > 0
    limit = MAX_RATE_PER_MINUTE.get(category, MAX_RATE_PER_MINUTE["default"])
    return (quantity / minutes) > limit


def scan_submission(submission: dict[str, Any], peer_quantities: list[float]) -> dict[str, Any]:
    """Evaluate one submission against physical limits and peer quantities."""
    reasons: list[str] = []

    qty = float(submission.get("quantity", 0) or 0)
    minutes = float(submission.get("duration_minutes", 0) or 0)
    category = submission.get("category", "default")

    if rate_anomaly(qty, minutes, category):
        reasons.append(f"Implausible rate: {qty} {submission.get('unit', 'units')} in {minutes} min")

    if peer_quantities and len(peer_quantities) >= 3:
        med = median(peer_quantities)
        mad = median([abs(v - med) for v in peer_quantities])
        if mad > 0 and abs(0.6745 * (qty - med) / mad) > Z_THRESHOLD:
            reasons.append(f"Quantity {qty} is a statistical outlier (median {med:.1f})")

    if qty < 0:
        reasons.append("Negative quantity")

    return {"flagged": len(reasons) > 0, "reasons": reasons}


def scan_batch(submissions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Scan a batch, using the batch itself as the peer group per category."""
    by_cat: dict[str, list[float]] = {}
    for submission in submissions:
        category = submission.get("category", "default")
        by_cat.setdefault(category, []).append(float(submission.get("quantity", 0) or 0))

    results = []
    for submission in submissions:
        peers = by_cat.get(submission.get("category", "default"), [])
        verdict = scan_submission(submission, peers)
        results.append({**submission, **verdict})
    return results
