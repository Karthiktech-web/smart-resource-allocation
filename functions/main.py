import functions_framework
import firebase_admin
from firebase_admin import firestore, messaging
from google.events.cloud.firestore_v1 import DocumentEventData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin once
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

@functions_framework.cloud_event
def on_critical_need(cloud_event):
    logger.info("--- TRIGGER: ON_CRITICAL_NEED (PROTOBUF VERSION) ---")
    
    try:
        # This handles the '0xbf' binary data correctly
        payload = DocumentEventData()
        payload._pb.ParseFromString(cloud_event.data)
        
        value = payload.value
        if not value:
            logger.error("No document value found in event.")
            return "OK"

        fields = value.fields

        # Extract values
        urgency = fields.get("urgency").string_value if "urgency" in fields else ""
        category = fields.get("category").string_value if "category" in fields else "unknown"
        location = fields.get("location_name").string_value if "location_name" in fields else "Unknown area"

        logger.info(f"Detected need: {category} in {location} with urgency: {urgency}")

        if urgency.lower() == "critical":
            # Get Coordinator Tokens
            users_ref = db.collection("users").where("role", "==", "coordinator")
            tokens = [u.to_dict().get("fcm_token") for u in users_ref.stream() if u.to_dict().get("fcm_token")]

            if tokens:
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=f"🚨 CRITICAL {category.upper()} NEED",
                        body=f"Urgent assistance required in {location}."
                    ),
                    tokens=tokens
                )
                messaging.send_each_for_multicast(message)
                logger.info(f"Sent notifications to {len(tokens)} coordinators.")
        
    except Exception as e:
        logger.error(f"Error in on_critical_need: {str(e)}")
    
    return "OK"

@functions_framework.cloud_event
def on_assignment_complete(cloud_event):
    logger.info("--- TRIGGER: ON_ASSIGNMENT_COMPLETE (PROTOBUF VERSION) ---")
    
    try:
        payload = DocumentEventData()
        payload._pb.ParseFromString(cloud_event.data)
        
        new_value = payload.value
        old_value = payload.old_value

        new_status = new_value.fields.get("status").string_value if "status" in new_value.fields else ""
        old_status = old_value.fields.get("status").string_value if "status" in old_value.fields else ""

        if new_status == "completed" and old_status != "completed":
            volunteer_id = new_value.fields.get("volunteer_id").string_value if "volunteer_id" in new_value.fields else ""
            
            hours_field = new_value.fields.get("hours_spent")
            hours = 0.0
            if hours_field:
                hours = hours_field.double_value or float(hours_field.integer_value or 0)

            if volunteer_id:
                db.collection("volunteers").document(volunteer_id).update({
                    "tasks_completed": firestore.Increment(1),
                    "active_assignments": firestore.Increment(-1),
                    "total_hours": firestore.Increment(hours)
                })

            need_ids_field = new_value.fields.get("need_ids")
            if need_ids_field and need_ids_field.array_value:
                for nid_val in need_ids_field.array_value.values:
                    nid = nid_val.string_value
                    if nid:
                        db.collection("needs").document(nid).update({
                            "status": "resolved",
                            "updated_at": firestore.SERVER_TIMESTAMP
                        })
            logger.info("Stats updated and needs resolved.")

    except Exception as e:
        logger.error(f"Error in on_assignment_complete: {str(e)}")
        
    return "OK"