# Smart Resource Allocation - Deployment Guide

## Production URLs (Live Now ✅)

### Frontend
- **URL**: https://smart-resource-allocatio-ca554.web.app
- **Hosting**: Firebase Hosting
- **Status**: ✅ Deployed and Live

### Backend API
- **URL**: https://sra-backend-tyfmslwwzq-el.a.run.app
- **Hosting**: Google Cloud Run
- **Region**: asia-south1
- **Status**: ✅ Deployed and Live
- **Health Check**: https://sra-backend-tyfmslwwzq-el.a.run.app/health

---

## Quick Links for Reviewers/Judges

| Link | Purpose |
|------|---------|
| [Live Frontend](https://smart-resource-allocatio-ca554.web.app) | See the application in action |
| [GitHub Repository](https://github.com/Karthiktech-web/smart-resource-allocation) | Source code and history |
| [Backend Health](https://sra-backend-tyfmslwwzq-el.a.run.app/health) | Verify backend is running |
| [Firebase Console](https://console.firebase.google.com/project/smart-resource-allocatio-ca554) | Frontend deployment logs |
| [Google Cloud Console](https://console.cloud.google.com/run) | Backend deployment logs |

---

## How to Share This Project (Single Link)

**Share this GitHub repository link with your friend:**

```
https://github.com/Karthiktech-web/smart-resource-allocation
```

They can:
1. Clone the repository: `git clone https://github.com/Karthiktech-web/smart-resource-allocation.git`
2. See the live deployment at: https://smart-resource-allocatio-ca554.web.app
3. Read all documentation in the README.md

---

## Local Development Setup

### Prerequisites
- Node.js 18+
- Python 3.8-3.12
- Git

### Clone Repository
```bash
git clone https://github.com/Karthiktech-web/smart-resource-allocation.git
cd smart-resource-allocation
```

### Frontend Setup (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
- Frontend runs on: `http://localhost:5173`

### Backend Setup (FastAPI)
```bash
cd ../backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
- Backend runs on: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Environment Variables

Create `backend/.env`:
```env
GEMINI_API_KEY=<your-api-key>
CLOUD_STORAGE_BUCKET=<your-bucket>
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
GOOGLE_CLOUD_PROJECT=<your-project>
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=<your-key>
VITE_FIREBASE_AUTH_DOMAIN=<your-domain>
VITE_FIREBASE_PROJECT_ID=<your-project>
```

---

## Production Deployment

### Frontend (Firebase Hosting)
```bash
cd frontend
npm run build
firebase deploy --only hosting --project smart-resource-allocatio-ca554
```

### Backend (Cloud Run)
```bash
cd backend
gcloud run deploy sra-backend \
  --source=. \
  --region=asia-south1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --set-env-vars="GEMINI_API_KEY=<key>,CLOUD_STORAGE_BUCKET=<bucket>"
```

---

## Testing the Deployment

### Backend Health
```bash
curl https://sra-backend-tyfmslwwzq-el.a.run.app/health
# Expected response: {"status":"ok"}
```

### Frontend Access
Simply visit: https://smart-resource-allocatio-ca554.web.app

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Smart Resource Allocation                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
   FRONTEND                                BACKEND
   (React + TypeScript + Vite)             (FastAPI + Python)
   ├─ Firebase Hosting                    ├─ Google Cloud Run
   ├─ Live at                             ├─ Live at
   │  https://smart-                      │  https://sra-backend-
   │  resource-allocatio-                 │  tyfmslwwzq-el.
   │  ca554.web.app                       │  a.run.app
   └─ 1.2MB bundle (348KB gzip)           └─ Poetry + Docker
```

---

## Key Technologies Used (Google Products)

1. ✅ **Google Cloud Run** - Backend hosting
2. ✅ **Firebase Hosting** - Frontend hosting
3. ✅ **Firebase Authentication** - User auth
4. ✅ **Google Cloud Storage** - Image storage
5. ✅ **Google Gemini API** - AI processing
6. ✅ **Google Cloud Artifact Registry** - Container registry
7. ✅ **Google Cloud Build** - CI/CD

---

## Troubleshooting

### Backend not responding
```bash
# Check health
curl https://sra-backend-tyfmslwwzq-el.a.run.app/health

# View logs
gcloud run logs read sra-backend --region asia-south1
```

### Frontend build issues
```bash
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

### Environment variable issues
- Ensure `.env` files are in correct location
- Verify Cloud Run environment variables are set
- Check CORS configuration matches your domain

---

## Phase 4 Completion Status

✅ **All 4 Phases Complete**
- Phase 1: Core architecture
- Phase 2: Frontend features
- Phase 3: Testing & optimization
- Phase 4: Deployment & submission ready

**Deployment Date**: April 27, 2026  
**Status**: Production Ready ✅
