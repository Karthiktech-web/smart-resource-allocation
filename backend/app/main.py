import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# --- K3.6 IMPORTS ADDED HERE ---
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
# ------------------------------

from app.auth import require_auth
from app.database import get_db
from app.models import AllocationApproveRequest, ProgramCreate, ProgramResponse


class CloudRunFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        return json.dumps(log_entry)


handler = logging.StreamHandler()
handler.setFormatter(CloudRunFormatter())
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

logging.info("Backend started successfully")

app = FastAPI(
    title="Smart Resource Allocation API",
    description="""
AI-Powered Survey Digitization & Smart Volunteer Coordination.

## Core Flow
1. Upload survey data -> AI processes needs
2. Analyze areas -> priority scores
3. Recommend volunteer allocation
4. Track impact
""",
    version="2.0.0",
    docs_url="/docs",
)

# --- K3.6 LIMITER INITIALIZATION ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# ------------------------------------

cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "Smart Resource Allocation API",
        "version": "2.0.0",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Added limit: 3 reports per minute
@app.get("/api/analytics/report")
@limiter.limit("3/minute")
async def generate_ai_report(request: Request, days: int = 30) -> dict[str, Any]:
    from app.services.impact_reporter import generate_impact_report
    return await generate_impact_report(time_range_days=days)


@app.get("/api/analytics/reports/history")
async def get_report_history(limit: int = 10) -> list[dict[str, Any]]:
    from app.services.impact_reporter import get_past_reports
    return await get_past_reports(limit=limit)


@app.get("/api/analytics/trends")
async def get_trend_data(days: int = 30) -> dict[str, Any]:
    from app.services.analytics import get_trends
    return await get_trends(days=days)


@app.get("/api/analytics/efficiency")
async def get_efficiency() -> dict[str, Any]:
    from app.services.analytics import get_efficiency_metrics
    return await get_efficiency_metrics()


# Added limit: 5 predictions per minute
@app.get("/api/analytics/predictions")
@limiter.limit("5/minute")
async def get_predictions(request: Request) -> dict[str, Any]:
    from app.services.predictor import predict_area_risks
    return await predict_area_risks()


@app.get("/api/alerts")
async def get_alerts() -> dict[str, Any]:
    from app.services.alerts import generate_alerts
    return await generate_alerts()


@app.post("/api/programs", response_model=ProgramResponse)
async def create_program(
    program: ProgramCreate, user: dict[str, Any] = Depends(require_auth)
) -> ProgramResponse:
    db = get_db()
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "name": program.name,
        "organization": program.organization,
        "category": program.category,
        "description": program.description,
        "regions": program.regions,
        "survey_count": 0,
        "needs_discovered": 0,
        "status": "active",
        "created_at": timestamp,
        "updated_at": timestamp,
        "created_by": user.get("uid"),
    }

    ref = db.collection("programs").document()
    ref.set(record)

    return ProgramResponse(id=ref.id, **record)


@app.post("/api/allocation/approve")
async def approve_allocation(
    payload: AllocationApproveRequest, user: dict[str, Any] = Depends(require_auth)
) -> dict[str, Any]:
    db = get_db()
    approved_at = datetime.now(timezone.utc).isoformat()
    saved_assignments = 0

    for assignment in payload.assignments:
        assignment_record = {
            **assignment,
            "status": assignment.get("status", "approved"),
            "approved_at": approved_at,
            "approved_by": user.get("uid"),
        }
        db.collection("assignments").document().set(assignment_record)
        saved_assignments += 1

    return {
        "status": "approved",
        "approved_count": saved_assignments,
        "approved_at": approved_at,
    }


# Added limit: 5 uploads per minute
@app.post("/api/surveys/digitize")
@limiter.limit("5/minute")
async def digitize_survey(
    request: Request,
    file: UploadFile = File(...),
    program_id: str = Form(""),
    location_name: str = Form(""),
    lat: float = Form(0),
    lng: float = Form(0),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    return {
        "survey_id": file.filename or "",
        "raw_text": "Sample logic here",
        "message": "Upload accepted.",
        "uploaded_by": user.get("uid"),
    }