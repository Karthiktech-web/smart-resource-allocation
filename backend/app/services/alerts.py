from datetime import datetime
from app.database import get_db


async def generate_alerts():
    db = get_db()
    alerts = []

    try:
        for doc in db.collection("areas").stream():
            area = doc.to_dict()

            name = area.get("name", "Unknown Area")
            open_needs = area.get("open_needs", 0)
            volunteer_gap = area.get("volunteer_gap", 0)
            priority = area.get("area_priority", "medium")

            # 🚨 Critical alert
            if priority == "high" and open_needs >= 3:
                alerts.append({
                    "type": "critical",
                    "message": f"{name} has high priority needs requiring immediate action",
                    "area": name,
                    "timestamp": datetime.utcnow().isoformat()
                })

            # ⚠ Volunteer shortage
            if volunteer_gap >= 5:
                alerts.append({
                    "type": "warning",
                    "message": f"{name} has a volunteer shortage",
                    "area": name,
                    "timestamp": datetime.utcnow().isoformat()
                })

            # 📊 Needs spike
            if open_needs >= 5:
                alerts.append({
                    "type": "info",
                    "message": f"{name} has increasing number of open needs",
                    "area": name,
                    "timestamp": datetime.utcnow().isoformat()
                })

    except Exception as e:
        return {
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }

    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "generated_at": datetime.utcnow().isoformat()
    }