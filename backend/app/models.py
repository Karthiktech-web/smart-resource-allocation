from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProgramCreate(BaseModel):
    name: str
    organization: str
    category: str
    description: str
    regions: list[str]

class ProgramResponse(BaseModel):
    id: str
    name: str
    organization: str
    category: str
    description: str
    regions: list[str]
    survey_count: int = 0
    needs_discovered: int = 0
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class SurveyDigitizeResponse(BaseModel):
    survey_id: str
    raw_text: str
    translated_text: str
    language_detected: str
    sentiment: str
    ai_analysis: dict
    needs_extracted: list[dict]
    message: str

class SurveyResponse(BaseModel):
    id: str
    program_id: str
    location_name: str
    lat: float
    lng: float
    source_type: str
    raw_text: str
    translated_text: str
    language_detected: str
    ai_analysis: dict
    sentiment: str
    created_at: Optional[str] = None

class NeedCreate(BaseModel):
    title: str
    description: str
    category: str
    urgency: str
    location_name: str
    lat: float
    lng: float
    area_id: Optional[str] = None
    source_type: str = "manual"
    source_program_id: Optional[str] = None

class NeedResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    urgency: str
    location_name: str
    lat: float
    lng: float
    area_id: Optional[str] = None
    source_type: str
    source_program_id: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_priority_score: Optional[float] = None
    status: str = "open"
    assigned_volunteers: list[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class AreaResponse(BaseModel):
    id: str
    name: str
    district: str
    state: str
    lat: float
    lng: float
    total_needs: int = 0
    open_needs: int = 0
    critical_needs_count: int = 0
    needs_by_category: dict = {}
    compound_score: float = 0.0
    area_priority: str = "low"
    programs_active: list[str] = []
    volunteers_assigned: int = 0
    volunteers_recommended: int = 0
    volunteer_gap: int = 0
    ai_insights: list[str] = []
    last_analyzed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class HeatMapPoint(BaseModel):
    lat: float
    lng: float
    weight: float
    area_name: str
    compound_score: float
    critical_needs: int
    total_needs: int

class VolunteerCreate(BaseModel):
    name: str
    email: str
    phone: str
    location_name: str
    lat: float
    lng: float
    skills: list[str]
    availability: str
    max_concurrent_assignments: int = 3

class VolunteerResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    location_name: str
    lat: float
    lng: float
    skills: list[str]
    availability: str
    total_hours: float = 0
    tasks_completed: int = 0
    reliability_score: float = 0.0
    active_assignments: int = 0
    categories_experienced: list[str] = []
    max_concurrent_assignments: int = 3
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class AssignmentResponse(BaseModel):
    id: str
    need_id: str
    volunteer_id: str
    volunteer_name: Optional[str] = None
    need_title: Optional[str] = None
    status: str = "pending"
    assigned_at: Optional[str] = None
    completed_at: Optional[str] = None

class AllocationRecommendation(BaseModel):
    need_id: str
    need_title: str
    need_category: str
    need_urgency: str
    recommended_volunteer_id: str
    recommended_volunteer_name: str
    match_score: float
    reasoning: str

class AllocationPlan(BaseModel):
    recommendations: list[AllocationRecommendation]
    total_needs_covered: int
    total_volunteers_used: int
    ai_summary: str

class AllocationApproveRequest(BaseModel):
    assignments: list[dict]

class ImpactLogCreate(BaseModel):
    category: str
    description: str
    people_helped: int
    volunteer_hours: float
    area_id: Optional[str] = None

class ImpactLogResponse(BaseModel):
    id: str
    category: str
    description: str
    people_helped: int
    volunteer_hours: float
    area_id: Optional[str] = None
    created_at: Optional[str] = None

class DashboardStats(BaseModel):
    total_programs: int
    total_surveys: int
    total_needs: int
    open_needs: int
    critical_needs: int
    total_volunteers: int
    active_volunteers: int
    total_areas: int
    critical_areas: int
    people_helped: int
    volunteer_hours: float
    needs_by_category: dict
    needs_by_urgency: dict
    recent_needs: list[dict]
    top_areas: list[dict]

class UserRegister(BaseModel):
    uid: str
    email: str
    name: str
    photo_url: Optional[str] = None
    role: str = "volunteer"

class UserResponse(BaseModel):
    uid: str
    email: str
    name: str
    photo_url: Optional[str] = None
    role: str
    created_at: Optional[str] = None