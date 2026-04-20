from datetime import datetime
import logging

from app.database import get_db
from app.services.gemini import analyze_area_portfolio

logger = logging.getLogger(__name__)


def _normalize_name(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _matches_area(need: dict, area_id: str, area_data: dict) -> bool:
    if need.get("area_id") == area_id:
        return True

    area_name = _normalize_name(area_data.get("name", ""))
    location_name = _normalize_name(need.get("location_name", ""))
    if area_name and location_name and (
        area_name in location_name or location_name in area_name
    ):
        return True

    try:
        lat_diff = abs(float(need.get("lat", 0)) - float(area_data.get("lat", 0)))
        lng_diff = abs(float(need.get("lng", 0)) - float(area_data.get("lng", 0)))
        if lat_diff < 0.35 and lng_diff < 0.35:
            return True
    except (TypeError, ValueError):
        return False

    return False


def _link_need_to_area_if_missing(need_ref, need: dict, area_id: str) -> None:
    if need.get("area_id"):
        return
    try:
        need_ref.update({"area_id": area_id, "updated_at": datetime.utcnow()})
    except Exception as exc:
        logger.warning("Failed to link need %s to area %s: %s", need_ref.id, area_id, exc)


async def analyze_area(area_id: str) -> dict:
    """
    Analyze one area across all matching needs, active programs, and nearby volunteers.
    """
    db = get_db()
    area_ref = db.collection("areas").document(area_id)
    area_doc = area_ref.get()
    if not area_doc.exists:
        raise ValueError(f"Area {area_id} not found")

    area_data = area_doc.to_dict()

    needs = []
    program_ids = set(area_data.get("programs_active", []))

    for need_doc in db.collection("needs").stream():
        need = need_doc.to_dict()
        if not _matches_area(need, area_id, area_data):
            continue

        _link_need_to_area_if_missing(
            db.collection("needs").document(need_doc.id),
            need,
            area_id,
        )

        need["id"] = need_doc.id
        needs.append(need)

        source_program_id = need.get("source_program_id")
        if source_program_id:
            program_ids.add(source_program_id)

    programs = []
    for program_id in program_ids:
        program_doc = db.collection("programs").document(program_id).get()
        if not program_doc.exists:
            continue
        program = program_doc.to_dict()
        program["id"] = program_doc.id
        programs.append(program)

    volunteers = []
    for volunteer_doc in db.collection("volunteers").stream():
        volunteer = volunteer_doc.to_dict()
        try:
            lat_diff = abs(float(volunteer.get("lat", 0)) - float(area_data.get("lat", 0)))
            lng_diff = abs(float(volunteer.get("lng", 0)) - float(area_data.get("lng", 0)))
        except (TypeError, ValueError):
            continue

        if lat_diff < 0.5 and lng_diff < 0.5:
            volunteer["id"] = volunteer_doc.id
            volunteers.append(volunteer)

    analysis = analyze_area_portfolio(
        area=area_data,
        needs=needs,
        programs=programs,
        volunteers=volunteers,
    )

    needs_by_category = {}
    open_needs = 0
    critical_needs = 0

    for need in needs:
        category = need.get("category", "other")
        needs_by_category[category] = needs_by_category.get(category, 0) + 1

        if need.get("status", "open") == "open":
            open_needs += 1
        if need.get("urgency") == "critical":
            critical_needs += 1

    volunteers_recommended = int(analysis.get("total_volunteers_recommended", 0) or 0)
    volunteers_assigned = int(area_data.get("volunteers_assigned", 0) or 0)

    update_data = {
        "compound_score": float(
            analysis.get("compound_score", area_data.get("compound_score", 0)) or 0
        ),
        "area_priority": analysis.get(
            "area_priority",
            area_data.get("area_priority", "low"),
        ),
        "ai_insights": analysis.get(
            "cross_program_insights",
            area_data.get("ai_insights", []),
        ),
        "volunteers_recommended": volunteers_recommended,
        "volunteer_gap": max(0, volunteers_recommended - volunteers_assigned),
        "total_needs": len(needs),
        "open_needs": open_needs,
        "critical_needs_count": critical_needs,
        "needs_by_category": needs_by_category,
        "programs_active": sorted(program_ids),
        "last_analyzed_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    area_ref.update(update_data)

    return {
        "area_id": area_id,
        "area_name": area_data.get("name", "Unknown"),
        "analysis": {
            **analysis,
            "volunteer_gap": update_data["volunteer_gap"],
            "needs_by_category": needs_by_category,
        },
        "needs_count": len(needs),
        "open_needs": open_needs,
        "critical_needs_count": critical_needs,
        "programs_count": len(programs),
        "volunteers_nearby": len(volunteers),
    }


async def analyze_all_areas() -> list[dict]:
    db = get_db()
    results = []

    for area_doc in db.collection("areas").stream():
        try:
            results.append(await analyze_area(area_doc.id))
        except Exception as exc:
            logger.exception("Area analysis failed for %s", area_doc.id)
            results.append({"area_id": area_doc.id, "error": str(exc)})

    return results
