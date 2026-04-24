from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import get_settings
from app.database import get_db
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def _get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            normalized = value.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _strip_json_fences(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _safe_percent(numerator: int, denominator: int) -> float:
    return round((numerator / max(denominator, 1)) * 100, 1)


def _read_collection(name: str) -> list[dict[str, Any]]:
    db = get_db()
    items: list[dict[str, Any]] = []
    for doc in db.collection(name).stream():
        item = doc.to_dict() or {}
        item["id"] = doc.id
        items.append(item)
    return items


def _filter_by_days(items: list[dict[str, Any]], field_name: str, time_range_days: int) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=time_range_days)
    filtered: list[dict[str, Any]] = []

    for item in items:
        parsed = _parse_datetime(item.get(field_name))
        if parsed is None or parsed >= cutoff:
            filtered.append(item)

    return filtered


def _within_days(value: Any, time_range_days: int) -> bool:
    parsed = _parse_datetime(value)
    if parsed is None:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(days=time_range_days)
    return parsed >= cutoff


def _build_fallback_report(
    *,
    time_range_days: int,
    total_people_helped: int,
    resolution_rate: float,
    total_volunteers: int,
    active_volunteers: int,
    total_hours: float,
    highest_priority_area: str,
    most_impacted_category: str,
    top_areas: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "title": "Smart Resource Allocation Impact Report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "time_range": f"{time_range_days} days",
        "executive_summary": (
            "This report was generated using fallback analytics because AI output "
            "was unavailable or could not be parsed. Core platform metrics are still included."
        ),
        "key_metrics": {
            "total_people_helped": total_people_helped,
            "needs_resolution_rate": f"{resolution_rate:.1f}%",
            "volunteer_utilization": f"{_safe_percent(active_volunteers, total_volunteers):.1f}%",
            "avg_response_time_days": 0,
            "most_impacted_category": most_impacted_category,
            "highest_priority_area": highest_priority_area,
        },
        "area_analysis": [
            {
                "area_name": area.get("name", "Unknown Area"),
                "priority": area.get("area_priority", "unknown"),
                "open_needs": area.get("open_needs", 0),
                "volunteer_gap": area.get("volunteer_gap", 0),
            }
            for area in top_areas
        ],
        "cross_program_insights": [
            "Cross-program analysis is available, but the AI-written narrative was not generated.",
            "Use area priority, volunteer gaps, and category distribution to guide near-term action.",
        ],
        "volunteer_performance": {
            "total_volunteers": total_volunteers,
            "total_volunteer_hours": total_hours,
        },
        "needs_trends": {
            "status": "Narrative trend analysis unavailable in fallback mode.",
        },
        "success_stories": [],
        "recommendations": [
            "Prioritize the highest-risk area for the next allocation cycle.",
            "Increase volunteer coverage in categories with the largest open need counts.",
            "Continue logging impact consistently to improve future AI reports.",
        ],
        "risk_alerts": [
            "Fallback mode was used for this report. Review Gemini configuration before stakeholder demos."
        ],
        "projected_impact": {
            "summary": "Projection unavailable in fallback mode.",
        },
    }


async def generate_impact_report(time_range_days: int = 30) -> dict[str, Any]:
    impact_logs = _filter_by_days(_read_collection("impact_logs"), "created_at", time_range_days)
    areas = _read_collection("areas")
    all_needs = _read_collection("needs")
    volunteers = _read_collection("volunteers")
    programs = _read_collection("programs")

    needs_created_in_range = _filter_by_days(all_needs, "created_at", time_range_days)
    open_needs = [need for need in needs_created_in_range if need.get("status") == "open"]
    assigned_needs = [
        need for need in needs_created_in_range if need.get("status") in {"assigned", "in_progress"}
    ]
    resolved_needs = [
        need
        for need in all_needs
        if need.get("status") == "resolved"
        and _within_days(need.get("updated_at") or need.get("created_at"), time_range_days)
    ]

    total_hours = sum(float(log.get("volunteer_hours", 0) or 0) for log in impact_logs)
    total_tasks = sum(int(volunteer.get("tasks_completed", 0) or 0) for volunteer in volunteers)
    total_people_helped = sum(int(log.get("people_helped", 0) or 0) for log in impact_logs)
    active_volunteers = len(
        [volunteer for volunteer in volunteers if int(volunteer.get("active_assignments", 0) or 0) > 0]
    )

    needs_by_category: dict[str, int] = {}
    for need in needs_created_in_range:
        category = need.get("category", "other")
        needs_by_category[category] = needs_by_category.get(category, 0) + 1

    needs_by_urgency: dict[str, int] = {}
    for urgency in ["critical", "high", "medium", "low"]:
        needs_by_urgency[urgency] = len(
            [need for need in needs_created_in_range if need.get("urgency") == urgency]
        )

    top_areas = sorted(areas, key=lambda area: area.get("compound_score", 0), reverse=True)[:5]
    highest_priority_area = top_areas[0].get("name", "Unknown") if top_areas else "Unknown"
    most_impacted_category = (
        max(needs_by_category.items(), key=lambda item: item[1])[0]
        if needs_by_category
        else "unknown"
    )
    resolution_rate = _safe_percent(len(resolved_needs), len(needs_created_in_range))

    prompt = f"""You are an expert impact analyst for an NGO volunteer coordination platform called Smart Resource Allocation (SRA).

Generate a COMPREHENSIVE IMPACT REPORT based on the following data:

SUMMARY STATISTICS:
- Total areas monitored: {len(areas)}
- Total programs active: {len(programs)}
- Total current volunteers: {len(volunteers)}
- Active volunteers right now: {active_volunteers}
- Needs discovered in last {time_range_days} days: {len(needs_created_in_range)}
- Open needs discovered in last {time_range_days} days: {len(open_needs)}
- Assigned/in-progress needs discovered in last {time_range_days} days: {len(assigned_needs)}
- Needs resolved in last {time_range_days} days: {len(resolved_needs)}
- Resolution rate: {resolution_rate:.1f}%
- Total volunteer hours logged in last {time_range_days} days: {total_hours}
- Total tasks completed: {total_tasks}
- Total people helped in last {time_range_days} days: {total_people_helped}
- Impact logs recorded in last {time_range_days} days: {len(impact_logs)}

AREAS DATA (top 5 by priority):
{json.dumps([
  {{
    "name": area.get("name"),
    "compound_score": area.get("compound_score", 0),
    "area_priority": area.get("area_priority"),
    "total_needs": area.get("total_needs", 0),
    "open_needs": area.get("open_needs", 0),
    "volunteers_assigned": area.get("volunteers_assigned", 0),
    "volunteer_gap": area.get("volunteer_gap", 0),
    "needs_by_category": area.get("needs_by_category", {{}})
  }}
  for area in top_areas
], indent=2, default=str)}

NEEDS BREAKDOWN BY CATEGORY:
{json.dumps(needs_by_category, indent=2, default=str)}

NEEDS BREAKDOWN BY URGENCY:
{json.dumps(needs_by_urgency, indent=2, default=str)}

Generate a professional impact report with these sections:

1. EXECUTIVE SUMMARY (2-3 paragraphs)
2. KEY METRICS
3. AREA ANALYSIS
4. CROSS-PROGRAM EFFECTIVENESS
5. VOLUNTEER PERFORMANCE
6. NEEDS TREND ANALYSIS
7. SUCCESS STORIES
8. RECOMMENDATIONS
9. RISK ALERTS
10. PROJECTED IMPACT

Write in a professional yet accessible tone suitable for NGO coordinators and potential donors.
Include specific numbers and percentages throughout.

Respond in JSON format:
{{
  "title": "...",
  "generated_at": "...",
  "time_range": "{time_range_days} days",
  "executive_summary": "...",
  "key_metrics": {{
    "total_people_helped": 0,
    "needs_resolution_rate": "0%",
    "volunteer_utilization": "0%",
    "avg_response_time_days": 0,
    "most_impacted_category": "...",
    "highest_priority_area": "..."
  }},
  "area_analysis": [...],
  "cross_program_insights": [...],
  "volunteer_performance": {{...}},
  "needs_trends": {{...}},
  "success_stories": [...],
  "recommendations": [...],
  "risk_alerts": [...],
  "projected_impact": {{...}}
}}"""

    report = _build_fallback_report(
        time_range_days=time_range_days,
        total_people_helped=total_people_helped,
        resolution_rate=resolution_rate,
        total_volunteers=len(volunteers),
        active_volunteers=active_volunteers,
        total_hours=total_hours,
        highest_priority_area=highest_priority_area,
        most_impacted_category=most_impacted_category,
        top_areas=top_areas,
    )

    settings = get_settings()
    if settings.gemini_api_key:
        try:
            client = _get_client()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                ),
            )
            report = json.loads(_strip_json_fences(response.text))
        except json.JSONDecodeError as exc:
            logger.error("Impact report JSON parse error: %s", exc)
        except Exception as exc:
            logger.error("Impact report generation failed: %s", exc)
    else:
        logger.warning("Gemini API key is not configured; using fallback impact report.")

    db = get_db()
    report_doc = {
        "report": report,
        "generated_at": datetime.now(timezone.utc),
        "time_range_days": time_range_days,
        "raw_stats": {
            "total_areas": len(areas),
            "total_programs": len(programs),
            "current_total_needs": len(all_needs),
            "needs_discovered_in_range": len(needs_created_in_range),
            "open_needs": len(open_needs),
            "assigned_needs": len(assigned_needs),
            "resolved_needs_in_range": len(resolved_needs),
            "total_volunteers": len(volunteers),
            "active_volunteers": active_volunteers,
            "volunteer_hours_in_range": total_hours,
            "total_people_helped": total_people_helped,
        },
    }

    ref = db.collection("reports").document()
    ref.set(report_doc)

    if isinstance(report, dict):
        report["report_id"] = ref.id

    return report


async def get_past_reports(limit: int = 10) -> list[dict[str, Any]]:
    reports = _read_collection("reports")
    reports.sort(
        key=lambda report: _parse_datetime(report.get("generated_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return reports[:limit]
