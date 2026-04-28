# 🔧 Fix Google Sign-In - Complete Setup Guide

## ✅ What I Fixed

1. **Updated Firebase Configuration** - Now uses correct project `smart-resource-allocatio-ca554`
2. **Added Error Handling** - Shows user-friendly error messages
3. **Fixed Environment Variables** - Matches production deployment
4. **Added Loading State** - Better UX feedback during sign-in

## ⚙️ Now You Need to Enable Google Sign-In in Firebase Console

### Step 1: Go to Firebase Console
```
https://console.firebase.google.com/project/smart-resource-allocatio-ca554/authentication
```

### Step 2: Enable Google Sign-In
1. Click **"Authentication"** in left sidebar
2. Click **"Sign-in method"** tab
3. Find **"Google"** provider
4. Click the **Google** row
5. Toggle the switch to **ON** (blue)
6. Add your support email if prompted
7. Click **"Save"**

### Step 3: Configure Authorized Redirect URIs

These URLs tell Google where your app is running:

#### For Production:
Add this to Google Cloud Console:
```
https://smart-resource-allocatio-ca554.firebaseapp.com
```

#### For Local Development:
Add this:
```
http://localhost:5173
http://localhost:3000
```

**How to add them:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select project: **smart-resource-allocatio-ca554**
3. Go to **APIs & Services** → **Credentials**
4. Find OAuth 2.0 Client ID for web
5. Click edit
6. Add URIs to "Authorized redirect URIs"
7. Click **"Save"**

### Step 4: Verify Authorized Domains in Firebase

1. In Firebase Console → **Authentication** tab
2. Scroll down to **"Authorized domains"**
3. Should show:
   - `smart-resource-allocatio-ca554.firebaseapp.com` ✅
   - `localhost` (for development) ✅
4. If not listed, add them

---

## 🧪 Test Google Sign-In

### Option 1: Test Live
1. Open: https://smart-resource-allocatio-ca554.web.app
2. Click **"Sign in with Google"**
3. A popup should open for Google login
4. Select your Google account
5. Grant permission if prompted

### Option 2: Test Locally
```bash
cd frontend
npm run dev
```
Then open `http://localhost:5173` and test

---

## ❌ Troubleshooting

### Problem: Popup doesn't open
**Solution:**
- Check browser popup blocker settings
- Ensure authorized URIs are configured
- Clear browser cache and cookies
- Try incognito/private window

### Problem: "Configuration error" message
**Solution:**
- Verify Firebase project ID matches
- Check API key is correct
- Ensure Google provider is enabled

### Problem: Error in browser console about CORS
**Solution:**
- This is normal for Firebase Auth
- Google will handle CORS automatically

---

## 📋 Checklist

- [ ] Google Sign-In enabled in Firebase Console
- [ ] Authorized Redirect URIs configured
- [ ] Authorized domains added
- [ ] Frontend redeployed ✅ (Already done!)
- [ ] Test login on live site
- [ ] Test login on local site

---

## 🔐 Security Note

Your configuration is secure because:
- ✅ Secrets in `.env` files are gitignored
- ✅ Only legitimate domains allowed
- ✅ Firebase validates all requests
- ✅ Google OAuth handles authentication

---

## 📞 Quick Links

| Resource | Link |
|----------|------|
| Firebase Console | https://console.firebase.google.com |
| Google Cloud Console | https://console.cloud.google.com |
| Firebase Auth Docs | https://firebase.google.com/docs/auth |
| Live App | https://smart-resource-allocatio-ca554.web.app |

---

## ✨ After Setup

Once Google Sign-In is working:
1. Users can click "Sign in with Google"
2. Google popup opens
3. User selects account
4. Redirects back to app
5. User is logged in! ✅

---

**Updated**: April 28, 2026
**Status**: Frontend deployment ✅ | Firebase config pending your console setup ⏳
