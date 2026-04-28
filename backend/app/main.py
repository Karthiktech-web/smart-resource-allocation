import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, List

from fastapi import Depends, FastAPI, File, Form, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.auth import require_auth
from app.database import get_db
from app.models import AllocationApproveRequest, ProgramCreate, ProgramResponse

# --- Logging & Rate Limiter Setup ---
logging.basicConfig(level=logging.INFO)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Smart Resource Allocation API",
    description="AI-Powered Volunteer Coordination for Social Impact",
    version="2.0.0",
    docs_url="/docs",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,*"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== BASE ROUTES ====================

@app.get("/")
async def root():
    return {"status": "healthy", "service": "SRA API", "version": "2.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ==================== DATA GETTERS (CRITICAL FOR UI) ====================

@app.get("/api/dashboard")
async def get_dashboard():
    db = get_db()
    needs = list(db.collection("needs").stream())
    vols = list(db.collection("volunteers").stream())
    impact = list(db.collection("impact_logs").stream())
    
    return {
        "total_needs": len(needs),
        "open_needs": len([n for n in needs if n.to_dict().get("status") == "open"]),
        "critical_needs": len([n for n in needs if n.to_dict().get("urgency") == "critical"]),
        "total_volunteers": len(vols),
        "people_helped": sum([i.to_dict().get("people_helped", 0) for i in impact]),
        "surveys_digitized": len(list(db.collection("surveys").stream())),
        "programs_active": len(list(db.collection("programs").stream()))
    }

@app.get("/api/needs")
async def list_needs():
    db = get_db()
    return [{**doc.to_dict(), "id": doc.id} for doc in db.collection("needs").stream()]

@app.get("/api/areas/priorities")
async def get_priorities():
    db = get_db()
    # Sorted by priority score
    docs = db.collection("areas").order_by("compound_score", direction="DESCENDING").stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]

@app.get("/api/areas/heatmap/data")
async def get_heatmap_data():
    db = get_db()
    areas = db.collection("areas").stream()
    return [{"lat": a.to_dict().get("lat"), "lng": a.to_dict().get("lng"), "weight": a.to_dict().get("compound_score", 0)} for a in areas]

@app.get("/api/programs")
async def list_programs():
    db = get_db()
    return [{**doc.to_dict(), "id": doc.id} for doc in db.collection("programs").stream()]

@app.get("/api/volunteers")
async def list_volunteers():
    db = get_db()
    return [{**doc.to_dict(), "id": doc.id} for doc in db.collection("volunteers").stream()]

# ==================== AI & ANALYTICS ROUTES ====================

@app.get("/api/analytics/report")
@limiter.limit("3/minute")
async def generate_ai_report(request: Request, days: int = 30):
    from app.services.impact_reporter import generate_impact_report
    return await generate_impact_report(time_range_days=days)

@app.get("/api/analytics/reports/history")
async def get_report_history(limit: int = 10):
    from app.services.impact_reporter import get_past_reports
    return await get_past_reports(limit=limit)

@app.get("/api/analytics/trends")
async def get_trend_data(days: int = 30):
    from app.services.analytics import get_trends
    return await get_trends(days=days)

@app.get("/api/analytics/efficiency")
async def get_efficiency():
    from app.services.analytics import get_efficiency_metrics
    return await get_efficiency_metrics()

@app.get("/api/analytics/predictions")
@limiter.limit("5/minute")
async def get_predictions(request: Request):
    from app.services.predictor import predict_area_risks
    return await predict_area_risks()

@app.post("/api/areas/analyze")
async def trigger_analyze_areas():
    from app.services.area_analyzer import analyze_all_areas
    return await analyze_all_areas()

# ==================== WRITE ACTIONS (SECURED) ====================

@app.post("/api/programs", response_model=ProgramResponse)
async def create_program(
    program: ProgramCreate, user: dict = Depends(require_auth)
):
    db = get_db()
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {**program.dict(), "survey_count": 0, "needs_discovered": 0, "status": "active", "created_at": timestamp, "updated_at": timestamp, "created_by": user.get("uid")}
    ref = db.collection("programs").document()
    ref.set(record)
    return ProgramResponse(id=ref.id, **record)

@app.post("/api/allocation/approve")
async def approve_allocation(
    payload: AllocationApproveRequest, user: dict = Depends(require_auth)
):
    db = get_db()
    approved_at = datetime.now(timezone.utc).isoformat()
    for assignment in payload.assignments:
        assignment_record = {**assignment, "status": "approved", "approved_at": approved_at, "approved_by": user.get("uid")}
        db.collection("assignments").document().set(assignment_record)
    return {"status": "approved", "count": len(payload.assignments)}

@app.post("/api/surveys/digitize")
@limiter.limit("5/minute")
async def digitize_survey(
    request: Request,
    file: UploadFile = File(...),
    program_id: str = Form(""),
    location_name: str = Form(""),
    lat: float = Form(0),
    lng: float = Form(0),
    user: dict = Depends(require_auth),
):
    # This is where your Vision + Gemini logic lives
    return {"message": "Survey upload accepted", "survey_id": file.filename, "uploader": user.get("uid")}