# Phase 4 Master Checklist & Timeline - Teammate 4 Lead

## Phase 4 Overview

**Duration:** Day 13 (All Day) + Day 14 (Morning/Afternoon)  
**Goal:** Test deployed app, record 2-minute demo video, submit to Google  
**NO NEW FEATURES** — only testing, recording, and submission

---

## Day 13 Timeline (Testing & Deployment)

### Morning (10:00 AM - 12:00 PM)

#### Manjunadha — Seed Demo Data
- [ ] Run `python scripts/reset_demo_data.py` to clear Firestore
- [ ] Run `python seed_data_rich.py` to populate demo data
- [ ] Verify in Firebase Console:
  - [ ] 6 programs created
  - [ ] 8 areas created
  - [ ] 50+ needs created
  - [ ] 20+ volunteers created
  - [ ] 20+ impact logs created

#### Teammate 4 — Deploy Backend
- [ ] Push code: `git add . && git commit -m "Phase 4: Deploy" && git push`
- [ ] Deploy to Cloud Run: `gcloud run deploy sra-backend ...`
- [ ] Copy backend URL: `https://sra-backend-xxxxx-el.a.run.app`
- [ ] Test health: `curl https://sra-backend-xxxxx-el.a.run.app/health`

#### Teammate 4 — Deploy Frontend
- [ ] Update `.env.production` with backend URL
- [ ] Build: `npm run build`
- [ ] Deploy: `firebase deploy --only hosting`
- [ ] Test: Open `https://smart-resource-allocation-2026.web.app`

**Status Check (12:00 PM):**
- [ ] Manjunadha signals "data seeded"
- [ ] Teammate 4 signals "both apps deployed"
- [ ] Everyone confirms both URLs load

---

### Midday (12:00 PM - 2:00 PM)

#### Everyone — Run Assigned Tests

**Karthik Tests Backend API:**
- [ ] Run 10 tests from `backend/tests/` checklist
- [ ] Document any failures
- [ ] Report P0 bugs immediately

**Chandu Tests Frontend:**
- [ ] Test all navigation flows
- [ ] Check responsiveness on mobile
- [ ] Document any UI bugs
- [ ] Report P0 bugs immediately

**Manjunadha Tests Auth & Database:**
- [ ] Sign in with Google
- [ ] Verify data consistency
- [ ] Check security rules
- [ ] Report any access issues

**Teammate 4 Tests Infrastructure:**
- [ ] Run security audit: `python tests/security_audit.py`
- [ ] Run load test: `python tests/load_test.py`
- [ ] Check Cloud Run metrics
- [ ] Verify logs flowing

**Test Results Template:**
```
Tester: [Name]
Assigned Tests: [List]
Total Tests: [ ] / [ ]
Failures: [ ] (list below)
P0 Bugs: [ ] (list below)
P1 Bugs: [ ] (can skip for demo)
Ready to move to fix phase: YES / NO
```

---

### Afternoon (2:00 PM - 5:00 PM)

#### Everyone — Fix P0 Bugs

**If any P0 bug found:**
1. Assign to responsible person
2. Debug immediately
3. Create PR/commit
4. Redeploy
5. Retest

**Priority Fix Order:**
1. Backend crashes → Karthik fixes
2. Frontend blank pages → Chandu fixes
3. Auth broken → Manjunadha fixes
4. CORS errors → Teammate 4 fixes

**If all tests PASS:**
- Skip to "Keep Warm" section

---

### Late Afternoon (5:00 PM - 6:00 PM)

#### Everyone — Final Verification

- [ ] Run all security audits again
- [ ] Verify no new bugs introduced
- [ ] Check all pages load < 3 seconds
- [ ] Verify demo data visible everywhere
- [ ] Test critical flows end-to-end

**Team Sign-Off:**
```
Date/Time: _______________
Backend Ready: YES [ ] NO [ ]
Frontend Ready: YES [ ] NO [ ]
Data Ready: YES [ ] NO [ ]
All Tests PASS: YES [ ] NO [ ]
Proceed to Video Recording: YES [ ] NO [ ]

Signed: Karthik _____, Chandu _____, Manjunadha _____, Teammate 4 _____
```

---

### Evening (6:00 PM - 8:00 PM)

#### Teammate 4 — Keep Backend Warm

```bash
# Run this 30-60 minutes before demo video recording
BACKEND_URL="https://sra-backend-xxxxx-el.a.run.app"

curl $BACKEND_URL/health
curl $BACKEND_URL/api/dashboard
curl $BACKEND_URL/api/areas/priorities
curl $BACKEND_URL/api/allocation/recommend
```

**Why:** Warms up Gemini API and Cloud Run instances for demo

#### Chandu — Pre-load Frontend Tabs

Open these in browser 10 minutes before video:
1. Login page
2. Dashboard
3. Area detail (Anantapur)
4. Survey upload page
5. Allocation page
6. Impact dashboard
7. Reports page

---

## Day 14 Timeline (Video & Submission)

### Morning (9:00 AM - 12:00 PM)

#### Teammate 4 — Record Demo Video

- [ ] Set up OBS Studio or screen recorder
- [ ] Test audio/microphone
- [ ] Set resolution to 1080p
- [ ] Open production app in browser
- [ ] Keep script visible
- [ ] **RECORD VIDEO** (follow script exactly)
- [ ] Save as MP4
- [ ] Check timing (must be ≤ 2:00)

**Recording Notes:**
```
Attempt 1: [ ] PASS / [ ] FAIL — Issue: ________________
Attempt 2: [ ] PASS / [ ] FAIL — Issue: ________________
Attempt 3: [ ] PASS / [ ] FAIL — Issue: ________________

Final Video: __________________________ (file name)
Duration: _____ seconds
Quality: 1080p [ ] ✓
Audio Clear: [ ] ✓
No Errors: [ ] ✓
```

#### Teammate 4 — Upload to YouTube

- [ ] Go to https://www.youtube.com/upload
- [ ] Upload final MP4
- [ ] Set to UNLISTED (not private)
- [ ] Add title: "Smart Resource Allocation - Demo (Google Solution Challenge 2026)"
- [ ] Wait for processing
- [ ] Copy YouTube URL: `https://youtu.be/xxxxx`
- [ ] Share URL with team

---

### Midday (12:00 PM - 2:00 PM)

#### Chandu — Create Backup Slides (if needed)

- [ ] Create 8-10 slide deck in Google Slides
- [ ] Include: problem, solution, tech stack, team, SDGs
- [ ] Include actual app screenshots
- [ ] Save as PDF backup

#### Everyone — Practice Q&A

Review 12 judge questions from Q&A guide:
- [ ] Each person can answer any question
- [ ] Responses take < 30 seconds
- [ ] Mention key phrases: "visibility", "smart allocation", "AI correlation"
- [ ] Practice 2-3 times

---

### Afternoon (2:00 PM - 5:00 PM)

#### Karthik — Write Submission

Using submission guide, fill Google Solution Challenge portal:
- [ ] Project Title
- [ ] Short Description
- [ ] Detailed Description (500 words)
- [ ] SDGs (1, 10, 11, 17)
- [ ] All 12 Google technologies
- [ ] YouTube URL
- [ ] GitHub link
- [ ] Live app URL
- [ ] Team info
- [ ] Review for typos

#### Teammate 4 — Final Quality Checks

Before submission:
- [ ] Video is exactly 2:00 or under
- [ ] YouTube video is accessible (unlisted)
- [ ] GitHub repo is public
- [ ] Live app loads and works
- [ ] All links are correct
- [ ] Submit button ready

---

### Evening (5:00 PM - 8:00 PM)

#### Karthik — SUBMIT

- [ ] Final review of all fields
- [ ] Click SUBMIT on Google Solution Challenge portal
- [ ] **SCREENSHOT confirmation**
- [ ] Share confirmation with team

**Submission Confirmation:**
```
Submission Date/Time: _______________
Confirmation Number: _______________
YouTube URL: https://youtu.be/_________
GitHub: Verified [ ]
Live App: Verified [ ]
Team signed off: YES [ ]
```

#### Everyone — Celebrate! 🎉

---

## Critical Paths & Dependencies

```
Manjunadha Seeds Data
        ↓
   Everyone Tests
        ↓
  Fix Any P0 Bugs
        ↓
All Tests PASS
        ↓
Backend Warm for Demo
        ↓
Teammate 4 Records Video
        ↓
Upload to YouTube
        ↓
Karthik Fills Form
        ↓
SUBMIT (Karthik)
        ↓
     DONE! 🎉
```

**BLOCKER:** If data not seeded by 10:30 AM → everything else is delayed

**BLOCKER:** If tests fail after 4:00 PM → skip fixes, record with known issues

**BLOCKER:** If video over 2:00 → must re-record, no extensions

---

## Success Criteria

### Day 13 EOD
- ✅ Backend responds < 2 seconds
- ✅ Frontend loads < 3 seconds
- ✅ Demo data visible in all screens
- ✅ 0 P0 bugs remaining
- ✅ All tests PASS
- ✅ Video recording ready to start

### Day 14 EOD
- ✅ Video recorded (≤ 2:00)
- ✅ YouTube URL obtained
- ✅ Submission completed
- ✅ Confirmation received

---

## Roles & Responsibilities

| Person | Day 13 | Day 14 |
|--------|--------|--------|
| **Karthik** | Deploy backend, test API | Write submission, SUBMIT |
| **Chandu** | Test frontend, fix UI | Record video, prep slides |
| **Manjunadha** | Seed data, test database | Practice Q&A, backup |
| **Teammate 4** | Deploy frontend, test infra | Record video, upload YouTube |

---

## Emergency Contacts

If critical issues:
- Backend down: **Karthik** (fixes immediately)
- Frontend broken: **Chandu** (fixes immediately)
- Data issues: **Manjunadha** (fixes immediately)
- Deployment/video: **Teammate 4** (escalates)

---

## Final Checklist Before Submission

- [ ] All team members have read Phase 4 guide
- [ ] Day 13 timeline distributed
- [ ] Deployment scripts tested locally
- [ ] GCP project verified
- [ ] Firebase project verified
- [ ] Demo data script ready to run
- [ ] Video equipment checked (OBS, mic, screen)
- [ ] All 4 guides saved and accessible
- [ ] GitHub repo public
- [ ] Team WhatsApp/Slack active for day 13-14

---

**REMEMBER:**
- **2:00 MAX on video** (disqualified if over)
- **Submission is FINAL** (no edits after)
- **Quality over quantity** (focus on core demo, skip edge cases)
- **Team coordination is KEY** (Manjunadha's data is critical path)

---

*Phase 4 Complete — Last step before Google judges see your work!*
