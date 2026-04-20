# Phase 4 Quick Reference Card - Print & Tape to Monitor

## CRITICAL LINKS (Copy & Paste Ready)

### Google Cloud / Firebase
```
GCP Project: https://console.cloud.google.com/project/sra-backend-2026
Firebase Console: https://console.firebase.google.com/u/0/project/smart-resource-allocation-2026
Cloud Run: https://console.cloud.google.com/run?project=sra-backend-2026&region=asia-south1
Cloud Build: https://console.cloud.google.com/cloud-build?project=sra-backend-2026
Cloud Firestore: https://console.firebase.google.com/u/0/project/smart-resource-allocation-2026/firestore
```

### Development Environments
```
Frontend Dev: http://localhost:5173
Frontend Prod: https://smart-resource-allocation-2026.web.app
Backend Dev: http://localhost:8000
Backend Prod: https://sra-backend-xxxxx-el.a.run.app (will get after deploy)
```

### GitHub
```
Repo: https://github.com/Karthiktech-web/smart-resource-allocation
Branch: feature/devops-phase3 (current)
New PR: Will create after Phase 4 deployment
```

### YouTube
```
Channel: [Your YouTube channel URL]
Upload Page: https://www.youtube.com/upload
Video Title: "Smart Resource Allocation - Demo (Google Solution Challenge 2026)"
```

### Google Solution Challenge
```
Submission Portal: https://www.solutionchallenge.withgoogle.com/
Submission Deadline: [Check email for exact date/time]
```

---

## CRITICAL COMMANDS (Copy & Run)

### Day 13 Morning — Deploy Backend
```bash
cd c:/Users/wwwle/smart-resource-allocation/backend

# Verify poetry.lock exists
ls -la poetry.lock

# Deploy to Cloud Run
gcloud run deploy sra-backend \
    --image=gcr.io/sra-backend-2026/sra-backend:latest \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=1 \
    --max-instances=3 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=sra-backend-2026,ENVIRONMENT=production,CORS_ORIGINS=https://smart-resource-allocation-2026.web.app"

# Get service URL
gcloud run services describe sra-backend --region=asia-south1 | grep "Service URL"
```

### Day 13 Morning — Deploy Frontend
```bash
cd c:/Users/wwwle/smart-resource-allocation/frontend

# Build production
npm run build

# Deploy to Firebase
firebase deploy --only hosting

# Verify live
echo "Frontend: https://smart-resource-allocation-2026.web.app"
```

### Day 13 Afternoon — Run Tests
```bash
cd c:/Users/wwwle/smart-resource-allocation/backend

# Security audit
python tests/security_audit.py

# Load test
python tests/load_test.py

# Both together
python tests/security_audit.py && python tests/load_test.py
```

### Day 13 Evening — Keep Backend Warm (30 min before video)
```bash
BACKEND_URL="https://sra-backend-xxxxx-el.a.run.app"

curl $BACKEND_URL/health
curl $BACKEND_URL/api/dashboard
curl $BACKEND_URL/api/areas/priorities
```

### Day 14 Morning — Check Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sra-backend" \
    --limit=20 --format=json

# Or in terminal
gcloud run logs read sra-backend --region=asia-south1 --limit=50
```

---

## CRITICAL ENVIRONMENT VARIABLES

### Backend (.env.production)
```
GOOGLE_CLOUD_PROJECT=sra-backend-2026
ENVIRONMENT=production
CORS_ORIGINS=https://smart-resource-allocation-2026.web.app
GEMINI_API_KEY=[Already configured]
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
```

### Frontend (.env.production)
```
VITE_API_URL=https://sra-backend-xxxxx-el.a.run.app
VITE_FIREBASE_API_KEY=[Already configured]
VITE_FIREBASE_PROJECT_ID=smart-resource-allocation-2026
VITE_FIREBASE_AUTH_DOMAIN=smart-resource-allocation-2026.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://smart-resource-allocation-2026.firebaseio.com
VITE_FIREBASE_STORAGE_BUCKET=smart-resource-allocation-2026.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=[Already configured]
VITE_FIREBASE_APP_ID=[Already configured]
```

---

## CRITICAL URLS (Day 13)

After deployment, update these in bookmark bar:

```
Backend URL: https://sra-backend-xxxxx-el.a.run.app
     ↳ Health: https://sra-backend-xxxxx-el.a.run.app/health
     ↳ Dashboard: https://sra-backend-xxxxx-el.a.run.app/api/dashboard

Frontend URL: https://smart-resource-allocation-2026.web.app
     ↳ Login: https://smart-resource-allocation-2026.web.app/login
     ↳ Dashboard: https://smart-resource-allocation-2026.web.app/dashboard
     ↳ Areas: https://smart-resource-allocation-2026.web.app/areas
     ↳ Programs: https://smart-resource-allocation-2026.web.app/programs
     ↳ Allocation: https://smart-resource-allocation-2026.web.app/allocate
```

---

## TESTING CHECKLIST (Day 13, 2:00 PM)

### Backend Tests (Teammate 4)
- [ ] Health endpoint responds < 500ms
- [ ] CORS headers present
- [ ] Load test: < 50 failures in 300 requests
- [ ] Security audit: 0 critical issues
- [ ] Logs flowing in Cloud Logging

### Frontend Tests (Chandu)
- [ ] Page loads < 3 seconds
- [ ] Login works (Google Sign-In)
- [ ] All navigation links work
- [ ] Demo data visible on dashboard
- [ ] No console errors (F12 → Console)

### Data Tests (Manjunadha)
- [ ] 6 programs in Firestore
- [ ] 8 areas in Firestore
- [ ] 50+ needs in Firestore
- [ ] 20+ volunteers in Firestore
- [ ] Firebase rules allow public read

### Infrastructure Tests (Karthik)
- [ ] Cloud Run health check: Active
- [ ] Min instances: 1 (not 0)
- [ ] Cloud Build: Latest deployment ✓
- [ ] SSL certificate: Valid
- [ ] Auto-scaling configured

---

## VIDEO RECORDING CHECKLIST (Day 14)

### Setup (9:00 AM)
- [ ] OBS Studio or screen recorder open
- [ ] Microphone tested and working
- [ ] Screen resolution set to 1080p
- [ ] All browser tabs pre-loaded
- [ ] Script printed or visible on second screen
- [ ] Backend warmed (last 30 min)
- [ ] Timer visible (must be ≤ 2:00)

### Recording (9:30 AM)
- [ ] Click record
- [ ] Start timer (must be exactly 2:00)
- [ ] Follow script EXACTLY
- [ ] No pauses or "ums"
- [ ] Clear enunciation
- [ ] Mouse movements smooth
- [ ] No error messages visible
- [ ] Finish exactly at 2:00

### Post-Production (10:00 AM)
- [ ] Save as MP4
- [ ] Check file size (should be 100-300 MB)
- [ ] Verify audio is clear
- [ ] Verify timing ≤ 2:00
- [ ] Preview once before upload

### Upload (10:30 AM)
- [ ] Go to youtube.com
- [ ] Click CREATE → UPLOAD VIDEO
- [ ] Select MP4 file
- [ ] Wait for upload (2-5 min)
- [ ] Set to UNLISTED (critical!)
- [ ] Add title and description
- [ ] Copy YouTube URL
- [ ] Share URL with team

---

## SUBMISSION CHECKLIST (Day 14, 2:00 PM)

### Before Submission
- [ ] YouTube URL confirmed working
- [ ] GitHub repo confirmed public
- [ ] Live app loads and works
- [ ] All links tested
- [ ] Form fields filled
- [ ] No typos or grammar errors
- [ ] All SDGs selected (1, 10, 11, 17)
- [ ] All 12 Google techs listed

### Submission (Karthik only)
- [ ] Go to solutionchallenge.withgoogle.com
- [ ] Click CREATE NEW SOLUTION
- [ ] Fill all required fields
- [ ] Attach files if needed
- [ ] Review one more time
- [ ] **CLICK SUBMIT**
- [ ] Wait for confirmation
- [ ] **SCREENSHOT confirmation page**
- [ ] Share confirmation with team

### Post-Submission
- [ ] Save confirmation screenshot
- [ ] Save confirmation email
- [ ] Celebrate! 🎉

---

## IF SOMETHING BREAKS (Emergency Steps)

### Backend won't deploy
```bash
# Check error
gcloud run deploy sra-backend --help

# Fallback: Direct deploy
gcloud builds submit --tag gcr.io/sra-backend-2026/sra-backend:latest backend/
```

### Frontend won't deploy
```bash
# Clear cache
rm -rf frontend/dist
npm run build

# Force redeploy
firebase deploy --force
```

### CORS errors
```bash
# Check current CORS
curl -I -H "Origin: https://smart-resource-allocation-2026.web.app" \
  https://sra-backend-xxxxx-el.a.run.app/health
```

### Video over 2:00
**RE-RECORD IMMEDIATELY** — no extensions allowed

### Can't submit
- Take screenshot showing attempt
- Email Google Solution Challenge support
- Have backup plan ready

---

## PHONE CONTACTS (If Needed)

- **Karthik:** [Add number]
- **Chandu:** [Add number]
- **Manjunadha:** [Add number]
- **Teammate 4:** [Add number]

---

## DAY 13 TIMELINE (QUICK VIEW)

| Time | Task | Owner | Status |
|------|------|-------|--------|
| 10:00 | Seed data | Manjunadha | [ ] |
| 11:00 | Deploy backend | Teammate 4 | [ ] |
| 11:30 | Deploy frontend | Teammate 4 | [ ] |
| 12:00 | Verify both live | Everyone | [ ] |
| 12:30 | Run all tests | Everyone | [ ] |
| 14:00 | Fix P0 bugs if any | All | [ ] |
| 17:00 | Final verification | Everyone | [ ] |
| 17:30 | Keep backend warm | Teammate 4 | [ ] |

---

## DAY 14 TIMELINE (QUICK VIEW)

| Time | Task | Owner | Status |
|------|------|-------|--------|
| 09:00 | Setup recording | Teammate 4 | [ ] |
| 09:30 | Record video | Teammate 4 | [ ] |
| 10:00 | Save & verify | Teammate 4 | [ ] |
| 10:30 | Upload to YouTube | Teammate 4 | [ ] |
| 12:00 | Fill submission form | Karthik | [ ] |
| 14:00 | Final review | Everyone | [ ] |
| 15:00 | **SUBMIT** | Karthik | [ ] |

---

**Print this page and tape to your monitor. Reference it constantly Days 13-14.**

**Success = All checkboxes checked ✓ and SUBMITTED ✓✓✓**
