from google.cloud import firestore


db = firestore.Client()


def on_need_created(event, context):
    """Triggered when a new Firestore document is created in the needs collection."""
    value = event.get("value")
    if not value:
        return

    fields = value.get("fields", {})
    if isinstance(context, dict):
        resource = context.get("resource")
    else:
        resource = getattr(context, "resource", None)

    need_id = resource.split("/documents/")[-1] if resource else None
    area_ref = fields.get("area_ref", {}).get("stringValue")
    category = fields.get("category", {}).get("stringValue")
    status = fields.get("status", {}).get("stringValue")

    if not need_id or not area_ref:
        return

    summary = f"Need created: {category or 'unknown'} ({status or 'unknown'})"
    log_doc = {
        "need_id": need_id,
        "area_ref": area_ref,
        "summary": summary,
        "created_at": firestore.SERVER_TIMESTAMP,
    }

    db.collection("impact_logs").add(log_doc)
