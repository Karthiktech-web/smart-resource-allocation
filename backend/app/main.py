
"""
Smart Resource Allocation — Main FastAPI Application
All API endpoints for the platform.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import logging

from app.config import get_settings
from app.database import get_db
from app.models import (
    ProgramCreate, ProgramResponse,
    SurveyDigitizeResponse, SurveyResponse,
    NeedCreate, NeedResponse,
    AreaResponse, HeatMapPoint,
    VolunteerCreate, VolunteerResponse,
    AssignmentResponse,
    AllocationPlan, AllocationApproveRequest, AllocationRecommendation,
    ImpactLogCreate, ImpactLogResponse,
    DashboardStats,
    UserRegister, UserResponse,
)
from app.auth import verify_firebase_token, require_auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Resource Allocation API",
    description="AI-Powered Survey Digitization & Smart Volunteer Coordination",
    version="1.0.0",
)

# CORS — Allow frontend to call backend
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "https://smart-resource-allocation-2026.web.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================
# HEALTH CHECK
# =============================================
@app.get("/")
async def root():
    return {"status": "healthy", "service": "Smart Resource Allocation API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# =============================================
# PROGRAMS ENDPOINTS
# =============================================
@app.post("/api/programs", response_model=ProgramResponse)
async def create_program(program: ProgramCreate):
    """Create a new NGO program/drive."""
    db = get_db()
    doc_data = {
        **program.model_dump(),
        "survey_count": 0,
        "needs_discovered": 0,
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    ref = db.collection("programs").document()
    ref.set(doc_data)

    return ProgramResponse(id=ref.id, **program.model_dump())

@app.get("/api/programs", response_model=list[ProgramResponse])
async def list_programs():
    """List all programs."""
    db = get_db()
    docs = db.collection("programs").stream()
    programs = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        # Convert datetime fields to strings
        for field in ["created_at", "updated_at"]:
            if field in data and data[field]:
                data[field] = data[field].isoformat() if hasattr(data[field], 'isoformat') else str(data[field])
        programs.append(ProgramResponse(**data))
    return programs

@app.get("/api/programs/{program_id}", response_model=ProgramResponse)
async def get_program(program_id: str):
    """Get a single program by ID."""
    db = get_db()
    doc = db.collection("programs").document(program_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Program not found")
    data = doc.to_dict()
    data["id"] = doc.id
    for field in ["created_at", "updated_at"]:
        if field in data and data[field]:
            data[field] = data[field].isoformat() if hasattr(data[field], 'isoformat') else str(data[field])
    return ProgramResponse(**data)


# =============================================
# SURVEY DIGITIZATION ENDPOINTS
# =============================================
@app.post("/api/surveys/digitize", response_model=SurveyDigitizeResponse)
async def digitize_survey(
    file: UploadFile = File(...),
    program_id: str = Form(...),
    location_name: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
):
    """
    THE CORE AI PIPELINE:
    Upload a survey photo → OCR → Translation → NLP → Gemini Analysis → Needs Extraction
    """
    from app.services.vision import extract_text_from_image
    from app.services.translation import detect_and_translate
    from app.services.nlp import analyze_sentiment
    from app.services.gemini import analyze_survey
    from app.services.storage import upload_image

    logger.info(f"Processing survey for program {program_id} at {location_name}")

    # Read the uploaded file
    file_bytes = await file.read()

    # Step 1: Upload image to Cloud Storage
    try:
        image_url = upload_image(file_bytes, file.filename or "survey.jpg", file.content_type or "image/jpeg")
    except Exception as e:
        logger.warning(f"Image upload failed (non-critical): {e}")
        image_url = ""

    # Step 2: Cloud Vision OCR — extract text from image
    raw_text = extract_text_from_image(file_bytes)
    if not raw_text:
        raise HTTPException(status_code=400, detail="Could not extract text from image. Please upload a clearer image.")

    # Step 3: Cloud Translation — detect language and translate to English
    translation = detect_and_translate(raw_text)
    translated_text = translation["translated_text"]
    language_detected = translation["language_detected"]

    # Step 4: Cloud NLP — sentiment analysis
    sentiment = analyze_sentiment(translated_text)

    # Step 5: Gemini AI — extract structured needs
    ai_analysis = analyze_survey(translated_text, sentiment, location_name)
    needs_extracted = ai_analysis.get("needs_extracted", [])

    # Step 6: Save survey to Firestore
    db = get_db()
    survey_data = {
        "program_id": program_id,
        "location_name": location_name,
        "lat": lat,
        "lng": lng,
        "source_type": "photo",
        "image_urls": [image_url] if image_url else [],
        "raw_text": raw_text,
        "translated_text": translated_text,
        "language_detected": language_detected,
        "ai_analysis": ai_analysis,
        "sentiment": sentiment["label"],
        "created_at": datetime.utcnow(),
    }
    survey_ref = db.collection("surveys").document()
    survey_ref.set(survey_data)

    # Step 7: Save each extracted need to Firestore
    saved_needs = []
    for need in needs_extracted:
        need_data = {
            "title": need.get("description", "Untitled need")[:100],
            "description": need.get("description", ""),
            "category": need.get("category", "other"),
            "urgency": need.get("urgency", "medium"),
            "location_name": location_name,
            "lat": lat,
            "lng": lng,
            "source_type": "ai_discovered",
            "source_program_id": program_id,
            "ai_confidence": need.get("confidence", 0.5),
            "ai_priority_score": _urgency_to_score(need.get("urgency", "medium")),
            "status": "open",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        need_ref = db.collection("needs").document()
        need_ref.set(need_data)
        saved_needs.append({**need, "id": need_ref.id})

    # Step 8: Update program survey count
    program_ref = db.collection("programs").document(program_id)
    program_doc = program_ref.get()
    if program_doc.exists:
        prog_data = program_doc.to_dict()
        program_ref.update({
            "survey_count": prog_data.get("survey_count", 0) + 1,
            "needs_discovered": prog_data.get("needs_discovered", 0) + len(needs_extracted),
            "updated_at": datetime.utcnow(),
        })

    logger.info(f"Survey processed: {len(needs_extracted)} needs extracted")

    return SurveyDigitizeResponse(
        survey_id=survey_ref.id,
        raw_text=raw_text,
        translated_text=translated_text,
        language_detected=language_detected,
        sentiment=sentiment["label"],
        ai_analysis=ai_analysis,
        needs_extracted=saved_needs,
        message=f"Successfully extracted {len(needs_extracted)} needs from survey",
    )


@app.get("/api/surveys", response_model=list[SurveyResponse])
async def list_surveys(program_id: Optional[str] = None):
    """List all surveys, optionally filtered by program."""
    db = get_db()
    query = db.collection("surveys")
    if program_id:
        query = query.where("program_id", "==", program_id)
    query = query.order_by("created_at", direction="DESCENDING").limit(50)

    surveys = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        if "created_at" in data and data["created_at"]:
            data["created_at"] = data["created_at"].isoformat() if hasattr(data["created_at"], 'isoformat') else str(data["created_at"])
        surveys.append(SurveyResponse(**data))
    return surveys


# =============================================
# NEEDS ENDPOINTS
# =============================================
@app.get("/api/needs", response_model=list[NeedResponse])
async def list_needs(
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    status: Optional[str] = None,
    area_id: Optional[str] = None,
    program_id: Optional[str] = None,
):
    """List needs with optional filters."""
    db = get_db()
    query = db.collection("needs")

    if category:
        query = query.where("category", "==", category)
    if urgency:
        query = query.where("urgency", "==", urgency)
    if status:
        query = query.where("status", "==", status)
    if area_id:
        query = query.where("area_id", "==", area_id)
    if program_id:
        query = query.where("source_program_id", "==", program_id)

    needs = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        for field in ["created_at", "updated_at"]:
            if field in data and data[field]:
                data[field] = data[field].isoformat() if hasattr(data[field], 'isoformat') else str(data[field])
        needs.append(NeedResponse(**data))
    return needs

@app.post("/api/needs", response_model=NeedResponse)
async def create_need(need: NeedCreate):
    """Manually create a need (in addition to AI-discovered needs)."""
    db = get_db()
    doc_data = {
        **need.model_dump(),
        "ai_confidence": 1.0,
        "ai_priority_score": _urgency_to_score(need.urgency),
        "status": "open",
        "assigned_volunteers": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    ref = db.collection("needs").document()
    ref.set(doc_data)
    return NeedResponse(id=ref.id, **need.model_dump(), status="open")

@app.patch("/api/needs/{need_id}")
async def update_need_status(need_id: str, status: str = Query(...)):
    """Update a need's status."""
    db = get_db()
    ref = db.collection("needs").document(need_id)
    doc = ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Need not found")
    ref.update({"status": status, "updated_at": datetime.utcnow()})
    return {"message": f"Need {need_id} updated to status: {status}"}


# =============================================
# AREAS ENDPOINTS
# =============================================
@app.get("/api/areas", response_model=list[AreaResponse])
async def list_areas():
    """List all areas with their aggregated data."""
    db = get_db()
    areas = []
    for doc in db.collection("areas").order_by("compound_score", direction="DESCENDING").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        for field in ["created_at", "updated_at", "last_analyzed_at"]:
            if field in data and data[field]:
                data[field] = data[field].isoformat() if hasattr(data[field], 'isoformat') else str(data[field])
        areas.append(AreaResponse(**data))
    return areas

@app.get("/api/areas/heatmap/data", response_model=list[HeatMapPoint])
async def get_heatmap_data():
    """Get heat map data points for Google Maps visualization."""
    db = get_db()
    points = []
    for doc in db.collection("areas").stream():
        data = doc.to_dict()
        points.append(HeatMapPoint(
            lat=data.get("lat", 0),
            lng=data.get("lng", 0),
            weight=data.get("compound_score", 1.0),
            area_name=data.get("name", "Unknown"),
            compound_score=data.get("compound_score", 0),
            critical_needs=data.get("critical_needs_count", 0),
            total_needs=data.get("total_needs", 0),
        ))
    return points

@app.get("/api/areas/{area_id}", response_model=AreaResponse)
async def get_area(area_id: str):
    """Get detailed area data including AI insights."""
    db = get_db()
    doc = db.collection("areas").document(area_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Area not found")
    data = doc.to_dict()
    data["id"] = doc.id
    for field in ["created_at", "updated_at", "last_analyzed_at"]:
        if field in data and data[field]:
            data[field] = data[field].isoformat() if hasattr(data[field], 'isoformat') else str(data[field])
    return AreaResponse(**data)

@app.get("/api/areas/{area_id}/insights")
async def get_area_insights(area_id: str):
    """Get AI-generated cross-program insights for an area."""
    from app.services.gemini import analyze_area

    db = get_db()
    area_doc = db.collection("areas").document(area_id).get()
    if not area_doc.exists:
        raise HTTPException(status_code=404, detail="Area not found")

    area_data = area_doc.to_dict()

    # Get needs for this area
    needs = []
    for doc in db.collection("needs").where("area_id", "==", area_id).stream():
        needs.append(doc.to_dict())

    # Get program names
    program_names = []
    for pid in area_data.get("programs_active", []):
        pdoc = db.collection("programs").document(pid).get()
        if pdoc.exists:
            program_names.append(pdoc.to_dict().get("name", "Unknown"))

    # Run Gemini analysis
    insights = analyze_area(
        area_name=area_data.get("name", "Unknown"),
        needs=needs,
        programs=program_names,
    )

    # Update area with new insights
    db.collection("areas").document(area_id).update({
        "compound_score": insights.get("compound_score", area_data.get("compound_score", 0)),
        "area_priority": insights.get("area_priority", area_data.get("area_priority", "medium")),
        "ai_insights": insights.get("ai_insights", []),
        "volunteers_recommended": insights.get("volunteers_recommended", 0),
        "last_analyzed_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })

    return insights


# =============================================
# VOLUNTEERS ENDPOINTS
# =============================================
@app.post("/api/volunteers", response_model=VolunteerResponse)
async def create_volunteer(volunteer: VolunteerCreate):
    """Register a new volunteer."""
    db = get_db()
    doc_data = {
        **volunteer.model_dump(),
        "total_hours": 0,
        "tasks_completed": 0,
        "reliability_score": 0.5,
        "active_assignments": 0,
        "categories_experienced": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    ref = db.collection("volunteers").document()
    ref.set(doc_data)
    return VolunteerResponse(id=ref.id, **volunteer.model_dump(), reliability_score=0.5)

@app.get("/api/volunteers", response_model=list[VolunteerResponse])
async def list_volunteers():
    """List all volunteers."""
    db = get_db()
    volunteers = []
    for doc in db.collection("volunteers").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        for field in ["created_at", "updated_at"]:
            if field in data and data[field]:
                data[field] = data[field].isoformat() if hasattr(data[field], 'isoformat') else str(data[field])
        volunteers.append(VolunteerResponse(**data))
    return volunteers

@app.get("/api/volunteers/{volunteer_id}", response_model=VolunteerResponse)
async def get_volunteer(volunteer_id: str):
    """Get a single volunteer."""
    db = get_db()
    doc = db.collection("volunteers").document(volunteer_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    data = doc.to_dict()
    data["id"] = doc.id
    for field in ["created_at", "updated_at"]:
        if field in data and data[field]:
            data[field] = data[field].isoformat() if hasattr(data[field], 'isoformat') else str(data[field])
    return VolunteerResponse(**data)


# =============================================
# ALLOCATION ENDPOINTS
# =============================================
@app.get("/api/allocation/recommend")
async def get_allocation_recommendations():
    """Get AI-recommended volunteer allocation plan."""
    from app.services.gemini import recommend_allocation

    db = get_db()

    # Get open needs
    needs = []
    for doc in db.collection("needs").where("status", "==", "open").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        needs.append(data)

    if not needs:
        return AllocationPlan(
            recommendations=[],
            total_needs_covered=0,
            total_volunteers_used=0,
            ai_summary="No open needs to allocate.",
        )

    # Get available volunteers
    volunteers = []
    for doc in db.collection("volunteers").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        if data.get("active_assignments", 0) < data.get("max_concurrent_assignments", 3):
            volunteers.append(data)

    if not volunteers:
        return AllocationPlan(
            recommendations=[],
            total_needs_covered=0,
            total_volunteers_used=0,
            ai_summary="No available volunteers for allocation.",
        )

    # Get AI recommendations
    ai_result = recommend_allocation(needs, volunteers)

    # Build response
    recommendations = []
    for rec in ai_result.get("recommendations", []):
        need_idx = rec.get("need_index", 1) - 1
        vol_idx = rec.get("volunteer_index", 1) - 1

        if 0 <= need_idx < len(needs) and 0 <= vol_idx < len(volunteers):
            need = needs[need_idx]
            vol = volunteers[vol_idx]
            recommendations.append(AllocationRecommendation(
                need_id=need["id"],
                need_title=need.get("title", "Unknown"),
                need_category=need.get("category", "other"),
                need_urgency=need.get("urgency", "medium"),
                recommended_volunteer_id=vol["id"],
                recommended_volunteer_name=vol.get("name", "Unknown"),
                match_score=rec.get("match_score", 0.5),
                reasoning=rec.get("reasoning", "AI-recommended match"),
            ))

    return AllocationPlan(
        recommendations=recommendations,
        total_needs_covered=len(recommendations),
        total_volunteers_used=len(set(r.recommended_volunteer_id for r in recommendations)),
        ai_summary=ai_result.get("summary", "Allocation plan generated."),
    )

@app.post("/api/allocation/approve")
async def approve_allocation(request: AllocationApproveRequest):
    """Approve allocation plan — create assignments."""
    db = get_db()
    created = []

    for assignment in request.assignments:
        need_id = assignment.get("need_id")
        volunteer_id = assignment.get("volunteer_id")

        if not need_id or not volunteer_id:
            continue

        # Create assignment
        assignment_data = {
            "need_id": need_id,
            "volunteer_id": volunteer_id,
            "status": "active",
            "assigned_at": datetime.utcnow(),
        }
        ref = db.collection("assignments").document()
        ref.set(assignment_data)

        # Update need status
        db.collection("needs").document(need_id).update({
            "status": "assigned",
            "updated_at": datetime.utcnow(),
        })

        # Update volunteer active assignments
        vol_doc = db.collection("volunteers").document(volunteer_id).get()
        if vol_doc.exists:
            vol_data = vol_doc.to_dict()
            db.collection("volunteers").document(volunteer_id).update({
                "active_assignments": vol_data.get("active_assignments", 0) + 1,
                "updated_at": datetime.utcnow(),
            })

        created.append({"assignment_id": ref.id, "need_id": need_id, "volunteer_id": volunteer_id})

    return {
        "message": f"Approved {len(created)} assignments",
        "assignments_created": created,
    }


# =============================================
# IMPACT ENDPOINTS
# =============================================
@app.post("/api/impact", response_model=ImpactLogResponse)
async def log_impact(impact: ImpactLogCreate):
    """Log an impact event."""
    db = get_db()
    doc_data = {
        **impact.model_dump(),
        "created_at": datetime.utcnow(),
    }
    ref = db.collection("impact_logs").document()
    ref.set(doc_data)
    return ImpactLogResponse(id=ref.id, **impact.model_dump())

@app.get("/api/impact", response_model=list[ImpactLogResponse])
async def list_impact_logs():
    """List all impact logs."""
    db = get_db()
    logs = []
    for doc in db.collection("impact_logs").order_by("created_at", direction="DESCENDING").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        if "created_at" in data and data["created_at"]:
            data["created_at"] = data["created_at"].isoformat() if hasattr(data["created_at"], 'isoformat') else str(data["created_at"])
        logs.append(ImpactLogResponse(**data))
    return logs

@app.get("/api/analytics/report")
async def get_analytics_report():
    """Generate AI-powered analytics report."""
    from app.services.gemini import generate_impact_report

    db = get_db()

    # Get all impact logs
    impact_logs = []
    for doc in db.collection("impact_logs").stream():
        impact_logs.append(doc.to_dict())

    # Get all areas
    areas = []
    for doc in db.collection("areas").stream():
        areas.append(doc.to_dict())

    report = generate_impact_report(impact_logs, areas)
    return report


# =============================================
# DASHBOARD ENDPOINT
# =============================================
@app.get("/api/dashboard", response_model=DashboardStats)
async def get_dashboard():
    """Get all dashboard statistics in one call."""
    db = get_db()

    # Count programs
    programs = list(db.collection("programs").stream())
    total_programs = len(programs)

    # Count surveys
    surveys = list(db.collection("surveys").stream())
    total_surveys = len(surveys)

    # Count and categorize needs
    needs_list = list(db.collection("needs").stream())
    total_needs = len(needs_list)
    open_needs = 0
    critical_needs = 0
    needs_by_category: dict[str, int] = {}
    needs_by_urgency: dict[str, int] = {}
    recent_needs = []

    for doc in needs_list:
        data = doc.to_dict()
        if data.get("status") == "open":
            open_needs += 1
        if data.get("urgency") == "critical":
            critical_needs += 1
        cat = data.get("category", "other")
        needs_by_category[cat] = needs_by_category.get(cat, 0) + 1
        urg = data.get("urgency", "medium")
        needs_by_urgency[urg] = needs_by_urgency.get(urg, 0) + 1
        recent_needs.append({
            "id": doc.id,
            "title": data.get("title", ""),
            "category": cat,
            "urgency": urg,
            "location_name": data.get("location_name", ""),
            "status": data.get("status", "open"),
        })

    # Sort recent needs by urgency
    urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recent_needs.sort(key=lambda x: urgency_order.get(x["urgency"], 4))
    recent_needs = recent_needs[:10]  # Top 10

    # Count volunteers
    volunteers = list(db.collection("volunteers").stream())
    total_volunteers = len(volunteers)
    active_volunteers = sum(1 for v in volunteers if v.to_dict().get("active_assignments", 0) > 0)

    # Count areas
    areas_list = list(db.collection("areas").stream())
    total_areas = len(areas_list)
    critical_areas = sum(1 for a in areas_list if a.to_dict().get("area_priority") == "critical")
    top_areas = []
    for doc in areas_list:
        data = doc.to_dict()
        top_areas.append({
            "id": doc.id,
            "name": data.get("name", ""),
            "compound_score": data.get("compound_score", 0),
            "area_priority": data.get("area_priority", "low"),
            "total_needs": data.get("total_needs", 0),
        })
    top_areas.sort(key=lambda x: x["compound_score"], reverse=True)
    top_areas = top_areas[:5]

    # Impact totals
    impact_logs = list(db.collection("impact_logs").stream())
    people_helped = sum(doc.to_dict().get("people_helped", 0) for doc in impact_logs)
    volunteer_hours = sum(doc.to_dict().get("volunteer_hours", 0) for doc in impact_logs)

    return DashboardStats(
        total_programs=total_programs,
        total_surveys=total_surveys,
        total_needs=total_needs,
        open_needs=open_needs,
        critical_needs=critical_needs,
        total_volunteers=total_volunteers,
        active_volunteers=active_volunteers,
        total_areas=total_areas,
        critical_areas=critical_areas,
        people_helped=people_helped,
        volunteer_hours=volunteer_hours,
        needs_by_category=needs_by_category,
        needs_by_urgency=needs_by_urgency,
        recent_needs=recent_needs,
        top_areas=top_areas,
    )


# =============================================
# AUTH ENDPOINTS
# =============================================
@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user: UserRegister):
    """Register or update a user after Google Sign-In."""
    db = get_db()
    user_ref = db.collection("users").document(user.uid)
    user_doc = user_ref.get()

    if user_doc.exists:
        # Update existing user
        user_ref.update({
            "name": user.name,
            "photo_url": user.photo_url,
            "updated_at": datetime.utcnow(),
        })
    else:
        # Create new user
        user_ref.set({
            **user.model_dump(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })

    return UserResponse(**user.model_dump())


# =============================================
# ASSIGNMENTS ENDPOINTS
# =============================================
@app.get("/api/assignments", response_model=list[AssignmentResponse])
async def list_assignments(
    volunteer_id: Optional[str] = None,
    status: Optional[str] = None,
):
    """List assignments with optional filters."""
    db = get_db()
    query = db.collection("assignments")
    if volunteer_id:
        query = query.where("volunteer_id", "==", volunteer_id)
    if status:
        query = query.where("status", "==", status)

    assignments = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        for field in ["assigned_at", "completed_at"]:
            if field in data and data[field]:
                data[field] = data[field].isoformat() if hasattr(data[field], 'isoformat') else str(data[field])
        assignments.append(AssignmentResponse(**data))
    return assignments


# =============================================
# HELPER FUNCTIONS
# =============================================
def _urgency_to_score(urgency: str) -> float:
    """Convert urgency level to a numeric score."""
    scores = {
        "critical": 9.0,
        "high": 7.0,
        "medium": 5.0,
        "low": 3.0,
    }
    return scores.get(urgency, 5.0)

