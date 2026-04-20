# Phase 4 Demo Video Recording Guide - Teammate 4

## Video Specifications

| Requirement | Value |
|------------|-------|
| **Duration** | 2 minutes MAXIMUM (will be disqualified if over) |
| **Format** | MP4 |
| **Resolution** | 1080p (1920x1080) |
| **Codec** | H.264 |
| **Audio** | Clear microphone, no background noise |
| **Platform** | YouTube (unlisted) |
| **Narration Script** | Follow provided script EXACTLY |

## Pre-Recording Checklist

- [ ] OBS Studio or ScreenFlow installed
- [ ] Microphone tested and working
- [ ] Recording resolution set to 1080p
- [ ] Browser has production app open in separate tabs
- [ ] Demo data is seeded in Firestore
- [ ] Backend is warm (no cold start)
- [ ] All pages pre-loaded (no loading delays)
- [ ] Screen recording app set to capture full screen
- [ ] Audio levels checked
- [ ] Quiet room, no background noise

## Recording Setup

### Using OBS Studio (Recommended)

1. **Download:** https://obsproject.com/download
2. **Settings:**
   - Scene → "Game Capture" or "Screen Capture"
   - Set resolution: 1920x1080
   - Set FPS: 60
   - Audio: Select your microphone
3. **Start recording**
4. **Follow the script below** (read narration as you demo)

### Using Windows 11 Built-in Recorder

1. Press **Win + Alt + R** to start
2. App will record current window
3. Stop with **Win + Alt + R**
4. Video saved to Videos folder

## Demo Video Script (2:00 MAX)

**READ THIS ALOUD WHILE RECORDING. TIME YOURSELF.**

```
[0:00-0:08] TITLE SCREEN
Show: Smart Resource Allocation app title/logo
Narrate: "Smart Resource Allocation — an AI-powered platform that 
         transforms how NGOs coordinate volunteer resources."

[0:08-0:25] PROBLEM
Click to: Show 3 different program names visible
Narrate: "Today, multiple NGOs work in the same areas but their data 
         is scattered across different programs. A water survey from 
         one organization doesn't talk to a health survey from another. 
         Resources get misallocated."

[0:25-0:40] VISIBILITY - Heat Map
Navigate to: Dashboard
Show: Heat map with red/yellow/green zones
Click on Anantapur (red zone)
Narrate: "SRA solves this by creating visibility. Our AI aggregates 
         data from ALL programs and shows coordinators where the real 
         needs are. Look — Anantapur is the highest priority."

[0:40-0:55] CROSS-PROGRAM INSIGHT
Show: Area detail page for Anantapur
Scroll to show: Multiple needs from different programs
Narrate: "When we click the area, we see needs from ALL programs 
         in one place. Our AI discovered that water contamination 
         is causing health problems — a pattern invisible to any 
         single organization."

[0:55-1:10] DATA INPUT - Survey Upload
Navigate to: Ingest/Upload page
Upload: A sample survey image (if available) or show upload UI
Narrate: "Data comes in through multiple channels. We can upload 
         handwritten surveys in regional languages. Our AI extracts 
         needs, translates to English, and structures the data 
         automatically."

[1:10-1:25] SMART ALLOCATION
Navigate to: Allocation/Recommend page
Click: "Generate AI Plan" or show recommendations
Show: Volunteer assignments with scores
Narrate: "This is where it gets powerful. Our allocation engine 
         analyzes priorities, volunteer skills, and proximity to 
         recommend optimal assignments."

[1:25-1:30] APPROVAL
Click: Approve or confirm allocation
Show: Success message
Narrate: "Volunteers are notified instantly."

[1:30-1:45] IMPACT TRACKING
Navigate to: Impact dashboard or Reports page
Show: Charts, efficiency scores, metrics
Narrate: "We track real impact — people helped, resolution rates, 
         volunteer efficiency. Our AI generates comprehensive reports."

[1:45-1:55] TECHNOLOGY & SDGs
Show: Brief mention of technology stack or SDG icons
Narrate: "Built on 12 Google Cloud services including Gemini AI, 
         Cloud Vision for OCR, Maps Platform for visualization, and 
         Firebase for real-time data."

[1:55-2:00] CLOSING
Show: Team/app name with SDG icons
Narrate: "Smart Resource Allocation — turning scattered data into 
         coordinated action. Addressing SDGs 1, 10, 11, and 17."
```

## Recording Tips

1. **Practice 3 times** before recording the final version
2. **Use a script** — read exactly as written
3. **Keep mouse movements smooth** and deliberate
4. **Click deliberately** (don't rapid-click)
5. **Zoom in** on important numbers (scores, counts)
6. **Let data load naturally** (don't show spinners)
7. **Record in one take** if possible
8. **If a section takes too long**, re-record just that section and edit
9. **Keep a timer visible** (use phone or watch) to stay under 2:00
10. **Review final video** — watch full length to check timing

## Post-Recording: Upload to YouTube

1. **Open:** https://www.youtube.com/upload
2. **Upload MP4 file**
3. **Title:** `Smart Resource Allocation - Demo (Google Solution Challenge 2026)`
4. **Description:** 
   ```
   Smart Resource Allocation - AI-powered volunteer coordination platform
   
   Demo video showing:
   - Multi-program data aggregation
   - Heat maps and area priority analysis
   - Cross-program pattern discovery
   - Smart volunteer allocation
   - Impact tracking
   
   Built with 12 Google Cloud services for the Google Solution Challenge 2026.
   
   GitHub: https://github.com/your-repo
   Live App: https://smart-resource-allocation-2026.web.app
   ```
5. **Visibility:** Set to **UNLISTED** (not private, not public)
6. **Copy URL** (format: https://youtu.be/xxxxx)
7. **Share URL with team** for submission

## Video Quality Checklist

Before uploading, verify:

- [ ] Video is exactly 2:00 or under
- [ ] Audio is clear and audible
- [ ] No background noise
- [ ] Resolution is 1080p
- [ ] No frozen frames
- [ ] Narration matches script
- [ ] All demo flows work (no errors)
- [ ] YouTube accepts upload
- [ ] URL is correct format

## Backup Plan

If live recording has issues:

1. **Record segments separately:**
   - Segment 1: Dashboard + Heat map (15 sec)
   - Segment 2: Area detail + Click-through (15 sec)
   - Segment 3: Survey upload (15 sec)
   - Segment 4: Allocation plan (15 sec)
   - Segment 5: Impact/Reports (15 sec)
   - Total: 75 seconds

2. **Edit together in:**
   - CapCut (free, easy)
   - DaVinci Resolve (free, powerful)
   - iMovie (Mac)
   - Any video editor

3. **Add voiceover:**
   - Record narration separately
   - Sync in editor
   - Export as one MP4

## Emergency Troubleshooting (Day 14)

| Problem | Quick Fix |
|---------|-----------|
| Video too long | Speed up playback 1.1x or trim excess |
| Audio unclear | Re-record audio track separately |
| Cold start visible | Record "waking up" separately, trim |
| Cursor distracting | Disable cursor in recording settings |
| Screen flicker | Check resolution/refresh rate settings |
| Upload fails | Try MP4 instead of MOV, check file size |

---

**Your phone/laptop may auto-lock during recording. Disable sleep settings before starting.**

**REMEMBER: 2:00 is the HARD LIMIT. Anything over will be rejected.**
