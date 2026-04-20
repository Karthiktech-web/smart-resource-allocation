import logging
import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =========================
# 🔹 Cloud Run Logging Setup
# =========================
class CloudRunFormatter(logging.Formatter):
    def format(self, record):
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

# =========================
# 🔹 FastAPI App
# =========================
app = FastAPI(
    title="Smart Resource Allocation API",
    description="""
AI-Powered Survey Digitization & Smart Volunteer Coordination.

## Core Flow
1. Upload survey data → AI processes needs  
2. Analyze areas → priority scores  
3. Recommend volunteer allocation  
4. Track impact  

## Tech Stack
- FastAPI  
- Google Cloud (Run, Storage, Vision, Gemini)  
- Firebase  
""",
    version="2.0.0",
    docs_url="/docs"
)

# =========================
# 🔹 CORS Configuration
# =========================
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔹 Basic Routes
# =========================
@app.get("/")
async def root():
    return {"status": "healthy", "service": "Smart Resource Allocation API", "version": "2.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}