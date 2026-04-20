# Smart Resource Allocation 🚀

AI-Powered Survey Digitization & Smart Volunteer Coordination  
Google Solution Challenge 2026 Project

---

## Problem

In rural India, multiple NGOs collect data but work in isolation:
- No shared visibility
- No prioritization of needs
- Poor volunteer allocation
- Paper-based surveys remain unused

---

## Solution

Smart Resource Allocation uses AI + Google Cloud to:

- Digitize surveys using OCR
- Translate regional languages
- Extract needs using AI
- Generate heatmaps of critical areas
- Recommend optimal volunteer allocation

---

## Tech Stack

### Frontend
- React + TypeScript
- Tailwind CSS

### Backend
- FastAPI (Python)
- Gemini API (AI processing)

### Cloud & DevOps
- Docker (containerization)
- Google Cloud Run (backend hosting)
- Firebase Hosting (frontend)
- GitHub Actions (CI/CD)

---

## Features

- 📷 Survey digitization (image → data)
- 🌐 Language translation
- 🧠 AI-based need extraction
- 🗺️ Heatmap visualization
- 🤝 Smart volunteer allocation

---

## Project Structure

## Phase 3 — Teammate 4 Deliverables

### Security Audit
- Added `backend/tests/security_audit.py` to validate exposed endpoints, CORS configuration, injection payload handling, rate limiting, write endpoint auth enforcement, and `.dockerignore` coverage.
- Run locally with:
  - `python backend/tests/security_audit.py`

### Load Testing
- Added `backend/tests/load_test.py` to simulate concurrent users across core read endpoints.
- Environment variables:
  - `SRA_BASE_URL` — default `http://127.0.0.1:8000`
  - `SRA_CONCURRENT_USERS` — default `10`
  - `SRA_REQUESTS_PER_USER` — default `5`
- Run locally with:
  - `python backend/tests/load_test.py`

### Build Optimization
- Added `rollup-plugin-visualizer` to `frontend/package.json`.
- Updated `frontend/vite.config.ts` to generate `dist/bundle-analysis.html` for bundle analysis.
- This supports Phase 3 optimization by identifying heavy packages and improving frontend bundle size.

### Staging / CI Readiness
- Existing GitHub Actions workflow lives in `.github/workflows/ci.yml`.
- Current pipeline includes backend setup, frontend install/build, and a placeholder deploy step.
- Phase 3 teammate 4 documentation now reflects security, load testing, and frontend optimization improvements.

### Notes
- `backend/.dockerignore` already excludes sensitive files such as `*.json`, `.env`, and local virtual environments.
- These scripts are intended for local or staging verification before production deployment.
