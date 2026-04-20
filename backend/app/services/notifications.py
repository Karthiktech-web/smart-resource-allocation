import json
import logging
from firebase_admin import messaging
from app.database import get_db

logger = logging.getLogger(__name__)


async def notify_volunteer_assigned(volunteer_id: str, area_name: str, action_steps: list) -> dict:
    db = get_db()
    volunteer_ref = db.collection("volunteers").document(volunteer_id)
    volunteer_doc = volunteer_ref.get()
    if not volunteer_doc.exists:
        return {"status": "volunteer_not_found"}

    volunteer = volunteer_doc.to_dict()
    token = volunteer.get("fcm_token")
    if not token:
        logger.info("No FCM token for volunteer %s", volunteer_id)
        return {"status": "no_token"}

    title = "New assignment approved"
    body = f"You have been assigned to {area_name}. Check your action steps."
    data_payload = {
        "type": "assignment",
        "area_name": area_name,
        "action_steps": json.dumps(action_steps),
    }

    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data=data_payload,
    )

    try:
        response = messaging.send(message)
        logger.info("Sent assignment notification to %s: %s", volunteer_id, response)
        return {"status": "sent", "response": response}
    except Exception as exc:
        logger.exception("Failed to send assignment notification to %s", volunteer_id)
        return {"status": "error", "error": str(exc)}


async def notify_urgent_need(area_name: str, category: str, urgency: str) -> dict:
    db = get_db()
    coordinators = []

    for user_doc in db.collection("users").where("role", "==", "coordinator").stream():
        user = user_doc.to_dict()
        token = user.get("fcm_token")
        if token:
            coordinators.append(token)

    if not coordinators:
        logger.info("No coordinator FCM tokens available for urgent need notification")
        return {"status": "no_tokens"}

    title = "Urgent need reported"
    body = f"{urgency.capitalize()} {category} need in {area_name}. Please respond urgently."
    multicast = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        tokens=coordinators,
        data={
            "type": "urgent_need",
            "area_name": area_name,
            "category": category,
            "urgency": urgency,
        },
    )

    try:
        response = messaging.send_multicast(multicast)
        logger.info("Sent urgent need notification to %s coordinators", response.success_count)
        return {
            "status": "sent",
            "success_count": response.success_count,
            "failure_count": response.failure_count,
        }
    except Exception as exc:
        logger.exception("Failed to send urgent need notifications")
        return {"status": "error", "error": str(exc)}
