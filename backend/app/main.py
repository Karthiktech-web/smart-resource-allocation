import logging
import json
from fastapi import FastAPI

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
# 🔹 Basic Routes
# =========================
@app.get("/")
def root():
    return {"message": "Smart Resource Allocation Backend Running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}