# Phase 4 Deployment Guide - Teammate 4

## Pre-Deployment Checklist

- [ ] Dockerfile updated to use Poetry
- [ ] cloudbuild.yaml updated with min-instances=1
- [ ] CORS configured in main.py
- [ ] .env.production has all required keys
- [ ] GCP project ID verified: `sra-backend-2026`
- [ ] Firebase project ID verified: `smart-resource-allocation-2026`

## GCP Project Configuration

```bash
# Set your GCP project
gcloud config set project sra-backend-2026

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
```

## Backend Deployment (Cloud Run)

### Option 1: Deploy using Cloud Build (CI/CD)
```bash
cd backend
git add .
git commit -m "Phase 4: Fix Dockerfile and CORS for production deployment"
git push origin feature/devops-phase3

# Trigger Cloud Build
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION=asia-south1 \
    .
```

### Option 2: Deploy directly to Cloud Run
```bash
cd backend

# Build image
docker build -t sra-backend:latest .

# Tag for GCR
docker tag sra-backend:latest gcr.io/sra-backend-2026/sra-backend:latest

# Push to GCR
docker push gcr.io/sra-backend-2026/sra-backend:latest

# Deploy
gcloud run deploy sra-backend \
    --image=gcr.io/sra-backend-2026/sra-backend:latest \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=1 \
    --max-instances=3 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=sra-backend-2026,GEMINI_API_KEY=$(cat .env.production | grep GEMINI_API_KEY | cut -d= -f2),CLOUD_STORAGE_BUCKET=sra-survey-images-2026,CORS_ORIGINS=https://smart-resource-allocation-2026.web.app,ENVIRONMENT=production"
```

### Get Backend URL
```bash
gcloud run services describe sra-backend --region=asia-south1 --format='value(status.url)'
# Copy the URL (e.g., https://sra-backend-xxxxx-el.a.run.app)
```

## Frontend Deployment (Firebase Hosting)

```bash
cd frontend

# Update production environment
cat > .env.production << EOF
VITE_API_URL=https://sra-backend-xxxxx-el.a.run.app
VITE_GOOGLE_MAPS_API_KEY=your-maps-api-key
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=smart-resource-allocation-2026.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=smart-resource-allocation-2026
VITE_FIREBASE_STORAGE_BUCKET=sra-survey-images-2026.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
EOF

# Build
npm run build

# Deploy
firebase deploy --only hosting:smart-resource-allocation-2026
```

### Get Frontend URL
```bash
firebase hosting:channel:list
# URL: https://smart-resource-allocation-2026.web.app
```

## Post-Deployment Verification

### Backend Health Check
```bash
BACKEND_URL=https://sra-backend-xxxxx-el.a.run.app

curl $BACKEND_URL/health
# Expected: {"status":"ok"}

curl $BACKEND_URL/
# Expected: {"status":"healthy", ...}
```

### Frontend Check
```bash
# Open in browser
https://smart-resource-allocation-2026.web.app
# Should load login page
```

### Keep Backend Warm (Before Demo)
```bash
# Run 30 minutes before demo to wake up Gemini API and Cloud Run

curl https://sra-backend-xxxxx-el.a.run.app/api/dashboard
curl https://sra-backend-xxxxx-el.a.run.app/api/areas/priorities
curl https://sra-backend-xxxxx-el.a.run.app/api/allocation/recommend
```

## Infrastructure Tests (Day 13)

All tests must PASS before moving to video recording.

```bash
# 1. Run security audit
cd backend
python tests/security_audit.py

# 2. Run load test
python tests/load_test.py

# 3. Verify logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sra-backend" --limit 10

# 4. Check Cloud Run metrics
gcloud monitoring time-series list --filter='resource.type=cloud_run_revision AND resource.labels.service_name=sra-backend'
```

## Troubleshooting

### Issue: Cold Start Delay
**Solution:** min-instances is already set to 1 in cloudbuild.yaml. Verify:
```bash
gcloud run services describe sra-backend --region=asia-south1 | grep minInstances
# Should show: minInstances: 1
```

### Issue: CORS Errors
**Solution:** Update CORS_ORIGINS environment variable:
```bash
gcloud run services update sra-backend \
    --region=asia-south1 \
    --update-env-vars=CORS_ORIGINS=https://smart-resource-allocation-2026.web.app
```

### Issue: 502 Bad Gateway
**Solution:** Check Cloud Run logs:
```bash
gcloud run services logs read sra-backend --region=asia-south1 --limit=50
```

### Issue: Container doesn't start
**Solution:** Verify Dockerfile build locally:
```bash
cd backend
docker build -t sra-backend:test .
docker run -p 8080:8080 sra-backend:test
# Should start without errors
```

## Deployment Timeline (Day 13)

| Time | Action | Owner |
|------|--------|-------|
| 10:00 | Manjunadha seeds demo data | Manjunadha |
| 10:30 | Deploy backend to Cloud Run | Teammate 4 |
| 11:00 | Deploy frontend to Firebase | Teammate 4 |
| 11:30 | Run infrastructure tests | Teammate 4 |
| 12:00 | Fix any P0 bugs | Everyone |
| 14:00 | All tests PASS, app warm | Teammate 4 |
| 18:00 | Final verification before demo | Everyone |

## Success Criteria (Day 14 Morning)

- ✅ Backend responds < 2 seconds
- ✅ Frontend loads in < 3 seconds
- ✅ Security audit shows no FAIL results
- ✅ Load test completes successfully
- ✅ Demo data visible in all screens
- ✅ Video ready to record
