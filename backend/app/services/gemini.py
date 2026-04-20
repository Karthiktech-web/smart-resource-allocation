"""
Gemini AI service - THE MOST IMPORTANT FILE IN THE PROJECT.
This is the FOURTH step in the AI pipeline:
  English Text + Sentiment -> [Gemini AI] -> Structured Needs + Insights

Gemini is used for:
1. Survey analysis - extracting structured needs from raw text
2. Area analysis - cross-program compound scoring
3. Allocation recommendations - optimal volunteer matching
4. Impact report generation - AI-written analytics
"""

from google import genai
from google.genai import types
from app.config import get_settings
import concurrent.futures
import json
import logging
import re

logger = logging.getLogger(__name__)


def _get_client() -> genai.Client:
    """Get Gemini client."""
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


def _normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def _local_need_recommendation(need: dict, volunteers: list[dict]) -> dict:
    if not volunteers:
        return {
            "recommendation": {
                "volunteer_index": 0,
                "match_score": 0,
                "reasoning": "No available volunteers to recommend.",
            },
            "summary": "No volunteers available for local fallback recommendation.",
        }

    need_category = _normalize_text(need.get("category"))
    best_score = -1.0
    best_index = 0
    best_volunteer = None

    for index, volunteer in enumerate(volunteers[:15]):
        score = float(volunteer.get("reliability_score", 0.5)) * 0.5
        volunteer_skills = [s.strip().lower() for s in volunteer.get("skills", []) if isinstance(s, str)]

        if need_category and need_category in volunteer_skills:
            score += 0.25

        if need.get("urgency") == "critical":
            score += 0.1

        try:
            lat1 = float(need.get("lat", 0) or 0)
            lng1 = float(need.get("lng", 0) or 0)
            lat2 = float(volunteer.get("lat", 0) or 0)
            lng2 = float(volunteer.get("lng", 0) or 0)
            distance = ((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) ** 0.5
            score += max(0.0, 0.2 - distance / 5)
        except (TypeError, ValueError):
            distance = None

        if score > best_score:
            best_score = score
            best_index = index
            best_volunteer = volunteer

    if not best_volunteer:
        return {
            "recommendation": {
                "volunteer_index": 0,
                "match_score": 0,
                "reasoning": "No suitable volunteer could be selected.",
            },
            "summary": "Local fallback recommendation was not able to select a volunteer.",
        }

    recommendation = {
        "volunteer_index": best_index + 1,
        "match_score": round(min(1.0, best_score), 2),
        "reasoning": (
            f"Selected {best_volunteer.get('name', 'a volunteer')} based on reliability"
            f" and skill match with the need category {need_category or 'unknown'}."
        ),
    }

    return {
        "recommendation": recommendation,
        "summary": "Local fallback recommendation used because the AI service was unavailable or timed out.",
    }


def analyze_survey(translated_text: str, sentiment: dict, location_name: str) -> dict:
    """
    Use Gemini to analyze a survey and extract structured needs.
    """
    client = _get_client()

    prompt = f"""You are an AI assistant analyzing community survey data for humanitarian resource allocation.

SURVEY TEXT:
{translated_text}

LOCATION: {location_name}
SENTIMENT: {sentiment.get('label', 'neutral')} (score: {sentiment.get('score', 0)})

TASK:
Extract all community needs from this survey.

Return ONLY valid JSON.
Do not use markdown.
Do not use triple backticks.
Do not include any explanation outside JSON.

Use exactly this schema:

{{
  "needs_extracted": [
    {{
      "category": "water",
      "urgency": "critical",
      "description": "Specific need description",
      "confidence": 0.95
    }}
  ],
  "summary": "Short summary of the survey",
  "key_themes": ["theme1", "theme2"]
}}

Rules:
- category must be one of: water, food, health, education, shelter, infrastructure
- urgency must be one of: critical, high, medium, low
- confidence must be a number between 0 and 1
- extract every distinct need mentioned
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )

        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

        result = json.loads(text)
        logger.info(f"Gemini extracted {len(result.get('needs_extracted', []))} needs")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned invalid JSON: {e}")

        fallback_needs = []
        lower_text = translated_text.lower()

        if any(word in lower_text for word in ["water", "bore well", "contaminated", "drinking water"]):
            fallback_needs.append({
                "category": "water",
                "urgency": "critical",
                "description": "Possible clean drinking water issue detected from survey text.",
                "confidence": 0.75,
            })

        if any(word in lower_text for word in ["food", "shortage", "hungry", "crops failed"]):
            fallback_needs.append({
                "category": "food",
                "urgency": "high",
                "description": "Possible food insecurity issue detected from survey text.",
                "confidence": 0.72,
            })

        if any(word in lower_text for word in ["health", "sick", "fever", "hospital", "treatment", "pregnant"]):
            fallback_needs.append({
                "category": "health",
                "urgency": "high",
                "description": "Possible healthcare access or illness issue detected from survey text.",
                "confidence": 0.73,
            })

        return {
            "needs_extracted": fallback_needs,
            "summary": "Used fallback extraction because AI returned invalid JSON.",
            "key_themes": ["fallback", "survey-analysis"],
        }

    except Exception as e:
        logger.error(f"Gemini survey analysis error: {e}")
        return {
            "needs_extracted": [],
            "summary": f"AI analysis failed: {str(e)}",
            "key_themes": [],
        }


def analyze_area(area_name: str, needs: list[dict], programs: list[str]) -> dict:
    client = _get_client()

    needs_summary = "\n".join([
        f"  - [{n.get('urgency', 'medium').upper()}] {n.get('category', 'unknown')}: {n.get('title', n.get('description', 'No description'))}"
        for n in needs
    ])

    prompt = f"""You are an AI analyst for humanitarian resource allocation.

AREA: {area_name}
ACTIVE PROGRAMS: {', '.join(programs)}

NEEDS IN THIS AREA:
{needs_summary}

TASK: Analyze this area for cross-program patterns and compute a compound priority score.

The compound score should consider:
1. Number and severity of needs
2. Cross-program correlations (e.g., water + health issues compound each other)
3. Vulnerability of affected populations
4. Gap between current resources and needs

Respond with ONLY valid JSON:
{{
  "compound_score": 8.5,
  "area_priority": "critical",
  "ai_insights": [
    "Cross-program insight about how needs interact...",
    "Another actionable insight..."
  ],
  "volunteers_recommended": 8,
  "key_correlations": ["water-health", "food-education"]
}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1024,
            ),
        )

        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        result = json.loads(text)
        logger.info(f"Area analysis for {area_name}: score={result.get('compound_score')}")
        return result

    except Exception as e:
        logger.error(f"Gemini area analysis error: {e}")
        return {
            "compound_score": 5.0,
            "area_priority": "medium",
            "ai_insights": [f"AI analysis unavailable: {str(e)}"],
            "volunteers_recommended": 3,
        }


def recommend_allocation(needs: list[dict], volunteers: list[dict]) -> dict:
    client = _get_client()

    needs_text = "\n".join([
        f"NEED-{i+1}: [{n.get('urgency', 'medium').upper()}] {n.get('category', 'unknown')} in {n.get('location_name', 'Unknown')} - {n.get('title', '')}"
        for i, n in enumerate(needs[:15])
    ])

    volunteers_text = "\n".join([
        f"VOL-{i+1}: {v.get('name', 'Unknown')} | Skills: {', '.join(v.get('skills', []))} | Location: {v.get('location_name', 'Unknown')} | Available: {v.get('availability', 'unknown')} | Reliability: {v.get('reliability_score', 0)}"
        for i, v in enumerate(volunteers[:15])
    ])

    prompt = f"""You are an AI engine for smart volunteer allocation.

OPEN NEEDS:
{needs_text}

AVAILABLE VOLUNTEERS:
{volunteers_text}

TASK:
Recommend the best volunteer for each need.

Return ONLY valid JSON.
Do not include markdown fences.
Do not include explanations outside JSON.
Use this exact schema:

{{
  "recommendations": [
    {{
      "need_index": 1,
      "volunteer_index": 1,
      "match_score": 0.92,
      "reasoning": "Why this volunteer is a good fit"
    }}
  ],
  "summary": "Overall allocation strategy summary",
  "unmatched_needs": [3, 5],
  "utilization_rate": 0.85
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )

        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

        result = json.loads(text)
        logger.info(f"Allocation: {len(result.get('recommendations', []))} matches")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Gemini allocation JSON parse error: {e}")

        fallback_recommendations = []
        for i, need in enumerate(needs[: min(len(needs), len(volunteers), 3)]):
            volunteer = volunteers[i]
            fallback_recommendations.append({
                "need_index": i + 1,
                "volunteer_index": i + 1,
                "match_score": 0.75,
                "reasoning": "Fallback allocation based on available volunteer ordering because AI response could not be parsed."
            })

        return {
            "recommendations": fallback_recommendations,
            "summary": "Used fallback allocation because AI returned invalid JSON.",
            "unmatched_needs": [],
            "utilization_rate": 0.5,
        }

    except Exception as e:
        logger.error(f"Gemini allocation error: {e}")
        return {
            "recommendations": [],
            "summary": f"AI allocation failed: {str(e)}",
            "unmatched_needs": [],
            "utilization_rate": 0,
        }


def recommend_need(need: dict, volunteers: list[dict]) -> dict:
    client = _get_client()

    need_text = f"NEED: [{need.get('urgency', 'medium').upper()}] {need.get('category', 'unknown')} at {need.get('location_name', 'Unknown')} - {need.get('title', '')}"
    volunteers_text = "\n".join([
        f"VOL-{i+1}: {v.get('name', 'Unknown')} | Skills: {', '.join(v.get('skills', []))} | Location: {v.get('location_name', 'Unknown')} | Available: {v.get('availability', 'unknown')} | Reliability: {v.get('reliability_score', 0)}"
        for i, v in enumerate(volunteers[:15])
    ])

    prompt = f"""You are an AI volunteer recommender for humanitarian response.

OPEN NEED:
{need_text}

AVAILABLE VOLUNTEERS:
{volunteers_text}

TASK:
Recommend the best volunteer for this need.

Return ONLY valid JSON.
Do not use markdown fences.
Do not include explanations outside JSON.
Use this exact schema:
{
  "recommendation": {
    "volunteer_index": 1,
    "match_score": 0.92,
    "reasoning": "Why this volunteer is a good fit"
  },
  "summary": "Overall recommendation summary"
}
"""

    def generate():
        return client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
            ),
        )

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(generate)
            response = future.result(timeout=15)

        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

        result = json.loads(text)
        return result

    except concurrent.futures.TimeoutError:
        logger.error("Gemini need recommendation request timed out")
        return _local_need_recommendation(need, volunteers)
    except json.JSONDecodeError as e:
        logger.error(f"Gemini need recommendation JSON parse error: {e}")
        return _local_need_recommendation(need, volunteers)
    except Exception as e:
        logger.error(f"Gemini need recommendation error: {e}")
        return _local_need_recommendation(need, volunteers)


def generate_impact_report(impact_logs: list[dict], areas: list[dict]) -> dict:
    client = _get_client()

    total_helped = sum(log.get("people_helped", 0) for log in impact_logs)
    total_hours = sum(log.get("volunteer_hours", 0) for log in impact_logs)
    categories_helped = {}
    for log in impact_logs:
        cat = log.get("category", "other")
        categories_helped[cat] = categories_helped.get(cat, 0) + log.get("people_helped", 0)

    prompt = f"""You are writing an impact report for a humanitarian resource allocation platform.

DATA:
- Total people helped: {total_helped}
- Total volunteer hours: {total_hours}
- Impact by category: {json.dumps(categories_helped)}
- Number of active areas: {len(areas)}
- Number of impact events: {len(impact_logs)}

TASK: Generate a compelling impact report with these sections:
1. Executive Summary (2-3 sentences)
2. Key Achievements (3-4 bullet points)
3. Areas of Highest Impact
4. Recommendations for next steps

Respond with ONLY valid JSON:
{{
  "executive_summary": "...",
  "key_achievements": ["achievement 1", "achievement 2"],
  "highest_impact_areas": ["area insight 1", "area insight 2"],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "overall_rating": "excellent"
}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=1024,
            ),
        )

        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        return json.loads(text)

    except Exception as e:
        logger.error(f"Gemini report error: {e}")
        return {
            "executive_summary": f"Report generation failed: {str(e)}",
            "key_achievements": [],
            "highest_impact_areas": [],
            "recommendations": [],
        }
def analyze_area_portfolio(
    area: dict,
    needs: list[dict],
    programs: list[dict],
    volunteers: list[dict],
) -> dict:
    """
    Richer Phase 2 area analysis that correlates needs across programs and
    recommends a volunteer skill mix for the area as a whole.
    """
    client = _get_client()

    area_summary = {
        "name": area.get("name", "Unknown"),
        "district": area.get("district", ""),
        "state": area.get("state", "Andhra Pradesh"),
        "population_affected": area.get("population_affected", "Unknown"),
        "current_compound_score": area.get("compound_score", 0),
        "current_area_priority": area.get("area_priority", "low"),
        "volunteers_assigned": area.get("volunteers_assigned", 0),
    }

    programs_summary = [
        {
            "name": program.get("name", "Unknown"),
            "category": program.get("category", "other"),
            "organization": program.get("organization", "Unknown"),
            "survey_count": program.get("survey_count", 0),
        }
        for program in programs
    ]

    needs_summary = [
        {
            "category": need.get("category", "other"),
            "urgency": need.get("urgency", "medium"),
            "status": need.get("status", "open"),
            "description": need.get("description", "")[:160],
            "source_program_id": need.get("source_program_id", ""),
            "ai_confidence": need.get("ai_confidence", 0),
        }
        for need in needs
    ]

    volunteers_summary = [
        {
            "name": volunteer.get("name", "Unknown"),
            "skills": volunteer.get("skills", []),
            "availability": volunteer.get("availability", "unknown"),
            "reliability_score": volunteer.get("reliability_score", 0),
            "active_assignments": volunteer.get("active_assignments", 0),
        }
        for volunteer in volunteers[:15]
    ]

    prompt = f"""You are an expert NGO operations analyst.

AREA:
{json.dumps(area_summary, indent=2)}

PROGRAMS ACTIVE IN THIS AREA:
{json.dumps(programs_summary, indent=2)}

DISCOVERED NEEDS ACROSS ALL PROGRAMS:
{json.dumps(needs_summary, indent=2)}

VOLUNTEERS NEAR THIS AREA:
{json.dumps(volunteers_summary, indent=2)}

TASK:
Perform cross-program analysis for this area and return ONLY valid JSON.
Do not use markdown fences.
Do not include any explanation outside JSON.

Use this exact schema:
{{
  "compound_score": 8.4,
  "area_priority": "critical",
  "cross_program_insights": [
    "Water and health needs are reinforcing each other across programs"
  ],
  "total_volunteers_recommended": 8,
  "skill_mix_needed": ["water sanitation", "community health"],
  "risk_factors": ["Contaminated water source", "Limited transport access"],
  "recommended_actions": [
    "Deploy a combined water-health response team first"
  ],
  "estimated_impact": "A coordinated intervention could reduce urgent risk for roughly 1,500 people."
}}

Rules:
- area_priority must be one of: critical, high, medium, low
- compound_score must be a number between 0 and 10
- skill_mix_needed, risk_factors, recommended_actions, and cross_program_insights must be arrays
- recommended_actions should be prioritized and practical
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )

        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

        result = json.loads(text)
        logger.info(
            "Gemini area portfolio analysis for %s: score=%s",
            area.get("name", "Unknown"),
            result.get("compound_score"),
        )
        return result

    except json.JSONDecodeError as e:
        logger.error("Gemini area portfolio JSON parse error: %s", e)
    except Exception as e:
        logger.error("Gemini area portfolio error: %s", e)

    # Fallback analysis if AI fails
    open_needs = [need for need in needs if need.get("status", "open") == "open"]
    critical_needs = [need for need in needs if need.get("urgency") == "critical"]
    categories = sorted({need.get("category", "other") for need in needs if need.get("category")})

    score = min(
        10.0,
        round(
            (len(open_needs) * 0.7) +
            (len(critical_needs) * 1.2) +
            (len(categories) * 0.4),
            1,
        ),
    )

    if score >= 8:
        priority = "critical"
    elif score >= 6:
        priority = "high"
    elif score >= 3:
        priority = "medium"
    else:
        priority = "low"

    insights = []
    if len(categories) > 1:
        insights.append(
            f"{len(categories)} need categories are overlapping in this area, which increases coordination complexity."
        )
    if critical_needs:
        insights.append(
            f"{len(critical_needs)} critical needs are still open and should be handled before lower urgency requests."
        )
    if not insights:
        insights.append("Area analysis used fallback scoring because AI analysis was unavailable.")

    return {
        "compound_score": score,
        "area_priority": priority,
        "cross_program_insights": insights,
    }
