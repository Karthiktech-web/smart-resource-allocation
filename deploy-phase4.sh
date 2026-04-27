# Phase 4 Deployment Script - Run this on Day 13
# Copy-paste these commands in order

echo "=== PHASE 4 DEPLOYMENT START ==="
echo "Time: $(date)"

# Set GCP project
echo "Setting GCP project..."
gcloud config set project sra-backend-2026

# Enable APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com

# Build and push Docker image
echo "Building Docker image..."
cd backend
docker build -t gcr.io/sra-backend-2026/sra-backend:latest .

echo "Pushing to GCR..."
docker push gcr.io/sra-backend-2026/sra-backend:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy sra-backend \
    --image=gcr.io/sra-backend-2026/sra-backend:latest \
    --region=asia-south1 \
    --platform=managed \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=1 \
    --max-instances=3 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=sra-backend-2026,ENVIRONMENT=production,CORS_ORIGINS=https://smart-resource-allocation-2026.web.app"

# Get backend URL
BACKEND_URL=$(gcloud run services describe sra-backend --region=asia-south1 --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"

# Deploy frontend
echo "Deploying frontend..."
cd ../frontend

# Create production env
cat > .env.production << EOF
VITE_API_URL=$BACKEND_URL
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=smart-resource-allocation-2026.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=smart-resource-allocation-2026
VITE_FIREBASE_STORAGE_BUCKET=sra-survey-images-2026.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
EOF

# Build and deploy
npm run build
firebase deploy --only hosting

echo "Frontend URL: https://smart-resource-allocation-2026.web.app"

# Warm up backend
echo "Warming up backend..."
curl $BACKEND_URL/health
curl $BACKEND_URL/api/dashboard
curl $BACKEND_URL/api/areas/priorities

echo "=== DEPLOYMENT COMPLETE ==="
echo "Backend: $BACKEND_URL"
echo "Frontend: https://smart-resource-allocation-2026.web.app"
echo "Next: Run Phase 4 tests from backend/scripts/phase4-testing-checklist.md"