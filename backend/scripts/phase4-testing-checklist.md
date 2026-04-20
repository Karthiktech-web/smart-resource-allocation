# Phase 4 Infrastructure Testing Checklist - Teammate 4

## Test Execution (Day 13)

All 10 infrastructure tests must PASS before proceeding to video recording.

### Backend URL (from deployment)
```
https://sra-backend-xxxxx-el.a.run.app
```

### Frontend URL
```
https://smart-resource-allocation-2026.web.app
```

---

## Test Suite 1: Cloud Run Service Health

### Test 1.1: Cloud Run Service Status
```bash
gcloud run services describe sra-backend --region=asia-south1
```
**Expected:**
- Status: Active
- Ingress: All (unauthenticated allowed)
- Min instances: 1
- Max instances: 3
- CPU: 1
- Memory: 512Mi

**Pass/Fail:** [ ]

### Test 1.2: Health Endpoint Response
```bash
curl https://sra-backend-xxxxx-el.a.run.app/health
```
**Expected:**
```json
{"status":"ok"}
```
**Response Time:** < 500ms

**Pass/Fail:** [ ]

### Test 1.3: Root Endpoint Response
```bash
curl https://sra-backend-xxxxx-el.a.run.app/
```
**Expected:**
```json
{"status":"healthy","service":"Smart Resource Allocation API","version":"2.0.0"}
```

**Pass/Fail:** [ ]

---

## Test Suite 2: Firebase Hosting & SSL

### Test 2.1: Frontend Loads
Open in browser:
```
https://smart-resource-allocation-2026.web.app
```
**Expected:**
- Page loads in < 3 seconds
- Login page visible
- No console errors

**Pass/Fail:** [ ]

### Test 2.2: SSL Certificate Valid
```bash
curl -I https://smart-resource-allocation-2026.web.app | grep HTTP
```
**Expected:**
```
HTTP/2 200
```
**No SSL warnings in browser (green padlock)**

**Pass/Fail:** [ ]

---

## Test Suite 3: CORS Configuration

### Test 3.1: CORS Headers Present
```bash
curl -H "Origin: https://smart-resource-allocation-2026.web.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS https://sra-backend-xxxxx-el.a.run.app/health \
     -v 2>&1 | grep "access-control"
```
**Expected:**
```
access-control-allow-origin: https://smart-resource-allocation-2026.web.app
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
```

**Pass/Fail:** [ ]

### Test 3.2: Frontend Calls Backend (No CORS Errors)
1. Open: https://smart-resource-allocation-2026.web.app
2. Open Developer Tools (F12)
3. Go to Network tab
4. Trigger an API call (e.g., click a button)
5. Check if any requests show "CORS" errors

**Expected:**
- No CORS errors in Network tab
- API calls return 200 or expected status

**Pass/Fail:** [ ]

---

## Test Suite 4: Response Performance

### Test 4.1: API Response Times
```bash
# Run 5 requests and measure time
for i in {1..5}; do
  time curl -s https://sra-backend-xxxxx-el.a.run.app/health > /dev/null
done
```
**Expected:**
- Average response time: < 1 second
- Max response time: < 2 seconds

**Pass/Fail:** [ ]

### Test 4.2: Frontend Page Load
1. Open: https://smart-resource-allocation-2026.web.app
2. Open DevTools → Lighthouse
3. Run Lighthouse audit
4. Check "Performance" score

**Expected:**
- Performance score: > 50
- LCP (Largest Contentful Paint): < 3 seconds

**Pass/Fail:** [ ]

---

## Test Suite 5: Console & Logs

### Test 5.1: No Browser Console Errors
1. Open: https://smart-resource-allocation-2026.web.app
2. Open DevTools (F12) → Console tab
3. Check for red errors

**Expected:**
- No red errors (warnings are OK)
- API calls succeed (green 200s)

**Pass/Fail:** [ ]

### Test 5.2: Cloud Run Logs Flowing
```bash
gcloud logging read "resource.type=cloud_run_revision AND \
  resource.labels.service_name=sra-backend" \
  --limit=10 \
  --format=json | head -20
```
**Expected:**
- Recent logs visible (within last 5 minutes)
- No ERROR or CRITICAL messages
- Requests are being logged

**Pass/Fail:** [ ]

---

## Test Suite 6: Docker & Build

### Test 6.1: Local Docker Build
```bash
cd backend
docker build -t sra-backend:test .
```
**Expected:**
- Build completes without errors
- Image size: < 500MB

**Pass/Fail:** [ ]

### Test 6.2: Docker Image Runs
```bash
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=sra-backend-2026 \
  sra-backend:test &

sleep 3
curl http://localhost:8080/health
kill %1
```
**Expected:**
```json
{"status":"ok"}
```

**Pass/Fail:** [ ]

---

## Test Suite 7: Environment Variables

### Test 7.1: Check Cloud Run Env Vars
```bash
gcloud run services describe sra-backend --region=asia-south1 | grep "environment"
```
**Expected:**
- GOOGLE_CLOUD_PROJECT: sra-backend-2026
- ENVIRONMENT: production
- CORS_ORIGINS: https://smart-resource-allocation-2026.web.app

**Pass/Fail:** [ ]

---

## Test Suite 8: Security Audit

### Test 8.1: Run Security Audit Script
```bash
cd backend
python tests/security_audit.py
```
**Expected:**
- PASS results (not FAIL)
- CORS restricted properly
- Injection payloads handled
- .dockerignore verified

**Pass/Fail:** [ ]

---

## Test Suite 9: Load Testing

### Test 9.1: Run Load Test
```bash
cd backend
python tests/load_test.py
```
**Expected:**
- 300 total requests
- Average response < 50ms
- Error rate < 10%
- Max response < 2 seconds

**Pass/Fail:** [ ]

---

## Test Suite 10: Demo Data Verification

### Test 10.1: Seed Data Present
1. Open Firebase Console
2. Go to Firestore Database
3. Check collections:

| Collection | Expected Count | Status |
|-----------|---|---|
| programs | 6 | [ ] |
| areas | 8 | [ ] |
| needs | 50+ | [ ] |
| volunteers | 20+ | [ ] |
| impact_logs | 20+ | [ ] |
| users | 4+ | [ ] |

---

## Master Test Summary

| Test # | Name | Status | Notes |
|--------|------|--------|-------|
| 1.1 | Cloud Run Status | [ ] | |
| 1.2 | Health Endpoint | [ ] | |
| 1.3 | Root Endpoint | [ ] | |
| 2.1 | Frontend Loads | [ ] | |
| 2.2 | SSL Certificate | [ ] | |
| 3.1 | CORS Headers | [ ] | |
| 3.2 | Frontend-Backend Call | [ ] | |
| 4.1 | Response Times | [ ] | |
| 4.2 | Frontend Performance | [ ] | |
| 5.1 | Console Errors | [ ] | |
| 5.2 | Cloud Logs | [ ] | |
| 6.1 | Docker Build | [ ] | |
| 6.2 | Docker Run | [ ] | |
| 7.1 | Env Variables | [ ] | |
| 8.1 | Security Audit | [ ] | |
| 9.1 | Load Test | [ ] | |
| 10.1 | Demo Data | [ ] | |

---

## Pass/Fail Criteria

### ✅ PASS = Ready for Video Recording
- ALL 17 tests marked PASS
- No P0 bugs remaining
- Backend response times < 2 seconds
- Frontend loads in < 3 seconds
- Demo data visible and correct

### ❌ FAIL = Fix Issues & Re-test
- Any test marked FAIL
- Any P0 bugs present
- Response times > 2 seconds
- Frontend errors visible
- Demo data missing

---

## Issue Resolution Log

If any test fails, document here:

| Test # | Issue | Root Cause | Fix Applied | Re-test Result |
|--------|-------|-----------|-------------|---|
| | | | | [ ] |
| | | | | [ ] |
| | | | | [ ] |

---

## Sign-Off (Day 13 Evening)

```
Infrastructure Testing Complete: [Date/Time]
All Tests PASS: [ ]
Backend Warm & Ready: [ ]
Frontend Live & Ready: [ ]
Demo Data Verified: [ ]
Video Recording Can Begin: [ ]

Signed: _____________________ (Teammate 4)
```

---

**If ANY test fails, DO NOT PROCEED to video recording. Fix it first.**

**Target completion: 2:00 PM Day 13**
