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
import json
import logging
import re

logger = logging.getLogger(__name__)


def _get_client() -> genai.Client:
    """Get Gemini client."""
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


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
