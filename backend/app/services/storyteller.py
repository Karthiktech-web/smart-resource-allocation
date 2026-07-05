"""NLG impact storyteller for completed tasks."""
from typing import Any


def build_prompt(task: dict[str, Any], proofs: list[dict[str, Any]], feedback: list[dict[str, Any]]) -> str:
    """Assemble a deterministic prompt from task data."""
    photos = len(proofs)
    comments = [item.get("comment", "") for item in feedback if item.get("comment")]
    ratings = [item.get("rating") for item in feedback if item.get("rating") is not None]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None
    return (
        "Write a concise, warm, donor-ready impact story (2-3 short paragraphs) for the "
        "completed relief task below. Be factual; do not invent numbers.\n\n"
        f"Task: {task.get('title')}\n"
        f"Category: {task.get('category')}\n"
        f"Quantity delivered: {task.get('quantity')} {task.get('unit', '')}\n"
        f"Location: {task.get('location_name') or task.get('area_id') or 'the field'}\n"
        f"Proof photos submitted: {photos}\n"
        f"Average beneficiary/volunteer rating: {avg_rating if avg_rating is not None else 'N/A'}\n"
        f"Volunteer comments: {'; '.join(comments) if comments else 'none'}\n"
    )


def generate_story(task: dict[str, Any], proofs: list[dict[str, Any]], feedback: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a narrative via Gemini, falling back to a deterministic template."""
    prompt = build_prompt(task, proofs, feedback)
    try:
        from app.services.gemini import _get_client
        from google.genai import types

        client = _get_client()
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        narrative = (resp.text or "").strip()
        if narrative:
            return {"narrative": narrative, "source": "gemini", "prompt": prompt}
    except Exception as error:
        return {
            "narrative": _fallback(task, proofs, feedback),
            "source": f"fallback ({error.__class__.__name__})",
            "prompt": prompt,
        }

    return {"narrative": _fallback(task, proofs, feedback), "source": "fallback", "prompt": prompt}


def _fallback(task: dict[str, Any], proofs: list[dict[str, Any]], feedback: list[dict[str, Any]]) -> str:
    return (
        f"Thanks to our partners, {task.get('quantity')} {task.get('unit', '')} of "
        f"{task.get('category', 'aid')} reached {task.get('location_name') or 'the community'}. "
        f"The delivery was documented with {len(proofs)} verified photo(s) and confirmed by "
        f"{len(feedback)} field report(s)."
    )
