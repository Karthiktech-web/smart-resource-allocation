"""Post-event PDF summary report generation."""
import io
from typing import Any

from app.services import events


def build_report_data(event: dict[str, Any], tasks: list[dict[str, Any]], proofs: list[dict[str, Any]], stories: list[dict[str, Any]]) -> dict[str, Any]:
    """Assemble the structured report payload (pure, testable)."""
    summary = events.aggregate_event(event, tasks, proofs)
    ev_stories = events.filter_for_event(stories, event)
    return {
        "event": {
            "name": event.get("name"),
            "venue": event.get("venue_name"),
            "start_at": event.get("start_at"),
            "end_at": event.get("end_at"),
        },
        "summary": summary,
        "stories": [
            {"narrative": s.get("narrative", ""), "task_id": s.get("task_id")}
            for s in ev_stories
        ],
    }


def render_pdf(report: dict[str, Any]) -> bytes:
    """Render the report payload to PDF bytes via reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Event Impact Report")
    styles = getSampleStyleSheet()
    flow: list[Any] = []

    ev = report["event"]
    flow.append(Paragraph(f"Event Impact Report: {ev.get('name', 'Event')}", styles["Title"]))
    flow.append(Paragraph(
        f"Venue: {ev.get('venue') or 'N/A'} &nbsp;|&nbsp; "
        f"{ev.get('start_at') or '?'} → {ev.get('end_at') or '?'}",
        styles["Normal"],
    ))
    flow.append(Spacer(1, 0.6 * cm))

    s = report["summary"]
    rows = [
        ["Metric", "Value"],
        ["Tasks total", s.get("tasks_total", 0)],
        ["Tasks verified", s.get("tasks_verified", 0)],
        ["Tasks in progress", s.get("tasks_in_progress", 0)],
        ["Quantity delivered", s.get("quantity_delivered", 0)],
        ["Proofs submitted", s.get("proofs_submitted", 0)],
        ["Progress", f"{s.get('progress_pct', 0)}%"],
    ]
    table = Table(rows, hAlign="LEFT", colWidths=[7 * cm, 7 * cm])
    flow.append(table)
    flow.append(Spacer(1, 0.6 * cm))

    flow.append(Paragraph("Impact Stories", styles["Heading2"]))
    if report["stories"]:
        for st in report["stories"]:
            flow.append(Paragraph(st["narrative"] or "(no narrative)", styles["Normal"]))
            flow.append(Spacer(1, 0.3 * cm))
    else:
        flow.append(Paragraph("No verified stories recorded for this event.", styles["Italic"]))

    doc.build(flow)
    return buf.getvalue()