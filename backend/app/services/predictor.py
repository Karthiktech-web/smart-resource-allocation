from datetime import datetime
from app.database import get_db


async def predict_area_risks() -> dict:
    db = get_db()  # ✅ correct way
    areas_data = []

    try:
        # 🔹 Fetch all areas
        for doc in db.collection("areas").stream():
            area = doc.to_dict()

            open_needs = area.get("open_needs", 0)
            volunteer_gap = area.get("volunteer_gap", 0)
            priority = area.get("area_priority", "medium")

            risks = []

            # 🔥 Rule-based prediction logic
            if open_needs >= 3:
                risks.append("High number of open needs may increase demand")

            if volunteer_gap >= 5:
                risks.append("Volunteer shortage may delay response")

            if priority == "high":
                risks.append("Critical area requires immediate attention")

            if not risks:
                risks.append("No immediate risk detected")

            areas_data.append({
                "area_name": area.get("name"),
                "district": area.get("district"),
                "risks": risks,
                "open_needs": open_needs,
                "volunteer_gap": volunteer_gap
            })

    except Exception as e:
        return {
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }

    return {
        "risk_predictions": areas_data,
        "early_warnings": [
            "Monitor high priority areas",
            "Increase volunteers where gap is high"
        ],
        "generated_at": datetime.utcnow().isoformat()
    }