import json
from datetime import datetime
from app.database import get_db
from app.services.gemini import recommend_allocation


async def generate_allocation_plan() -> dict:
    db = get_db()
    needs = []
    for doc in db.collection("needs").where("status", "==", "open").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        needs.append(data)

    volunteers = []
    for doc in db.collection("volunteers").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        if data.get("active_assignments", 0) < data.get("max_concurrent_assignments", 3):
            volunteers.append(data)

    if not needs:
        return {
            "plan_summary": "No open needs available for allocation.",
            "recommendations": [],
            "total_needs_covered": 0,
            "total_volunteers_used": 0,
            "utilization_rate": 0,
        }

    if not volunteers:
        return {
            "plan_summary": "No available volunteers for allocation.",
            "recommendations": [],
            "total_needs_covered": 0,
            "total_volunteers_used": 0,
            "utilization_rate": 0,
        }

    ai_result = recommend_allocation(needs, volunteers)
    recommendations = []

    for rec in ai_result.get("recommendations", []):
        need_idx = rec.get("need_index", 1) - 1
        vol_idx = rec.get("volunteer_index", 1) - 1

        if 0 <= need_idx < len(needs) and 0 <= vol_idx < len(volunteers):
            need = needs[need_idx]
            vol = volunteers[vol_idx]
            recommendations.append({
                "need_id": need["id"],
                "need_title": need.get("title", need.get("description", "Untitled need")),
                "need_category": need.get("category", "other"),
                "need_urgency": need.get("urgency", "medium"),
                "area_id": need.get("area_id"),
                "area_name": need.get("location_name", "Unknown"),
                "recommended_volunteer_id": vol["id"],
                "recommended_volunteer_name": vol.get("name", "Unknown"),
                "match_score": rec.get("match_score", 0.5),
                "reasoning": rec.get("reasoning", "AI-recommended match"),
            })

    return {
        "plan_summary": ai_result.get("summary", "Allocation plan generated."),
        "recommendations": recommendations,
        "total_needs_covered": len(recommendations),
        "total_volunteers_used": len(set(r["recommended_volunteer_id"] for r in recommendations)),
        "utilization_rate": ai_result.get("utilization_rate", 0),
    }


async def approve_allocation(allocations: list) -> dict:
    db = get_db()
    created = []

    for assignment in allocations:
        need_id = assignment.get("need_id")
        volunteer_id = assignment.get("volunteer_id")
        if not need_id or not volunteer_id:
            continue

        assignment_data = {
            "need_id": need_id,
            "volunteer_id": volunteer_id,
            "status": "active",
            "assigned_at": datetime.utcnow(),
        }
        ref = db.collection("assignments").document()
        ref.set(assignment_data)

        need_ref = db.collection("needs").document(need_id)
        need_doc = need_ref.get()
        if need_doc.exists:
            need_ref.update({"status": "assigned", "updated_at": datetime.utcnow()})
            need_data = need_doc.to_dict()
            area_id = need_data.get("area_id")
            if area_id:
                area_ref = db.collection("areas").document(area_id)
                area_doc = area_ref.get()
                if area_doc.exists:
                    area_ref.update({
                        "volunteers_assigned": area_doc.to_dict().get("volunteers_assigned", 0) + 1,
                        "updated_at": datetime.utcnow(),
                    })

        vol_ref = db.collection("volunteers").document(volunteer_id)
        vol_doc = vol_ref.get()
        if vol_doc.exists:
            vol_ref.update({
                "active_assignments": vol_doc.to_dict().get("active_assignments", 0) + 1,
                "updated_at": datetime.utcnow(),
            })

        created.append({"assignment_id": ref.id, "need_id": need_id, "volunteer_id": volunteer_id})

    return {
        "message": f"Approved {len(created)} assignments",
        "assignments_created": created,
    }


async def get_gap_report() -> dict:
    db = get_db()
    gaps = []

    for doc in db.collection("areas").stream():
        data = doc.to_dict()
        gap = int(data.get("volunteer_gap", 0) or 0)
        if gap > 0:
            gaps.append({
                "area_id": doc.id,
                "area_name": data.get("name", "Unknown"),
                "compound_score": data.get("compound_score", 0),
                "open_needs": data.get("open_needs", 0),
                "volunteers_assigned": data.get("volunteers_assigned", 0),
                "volunteer_gap": gap,
            })

    gaps.sort(key=lambda item: item["volunteer_gap"], reverse=True)
    return {"total_areas_with_gaps": len(gaps), "gaps": gaps}
