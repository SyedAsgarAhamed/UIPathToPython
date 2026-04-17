# Deployment Guide: RCC + GCP

## Prerequisites

1. **Install rcc** (Robocorp Command Center)
   ```bash
   # Windows
   choco install rcc
   # Or download from: https://downloads.robocorp.cloud/
   ```

2. **GCP Setup**
   - Google Cloud Project created
   - GCP CLI installed (`gcloud`)
   - Cloud Build API enabled
   - Container Registry API enabled

## Build Locally with RCC

### 1. Build the robot
```bash
rcc robot build --workspace . --output robot.zip
```

### 2. Verify build
```bash
rcc robot test --workspace . --task producer
rcc robot test --workspace . --task consumer
```

## Deploy to GCP

### Option 1: Using Cloud Build (Recommended)

1. **Connect GCP project**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Push to Cloud Build**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

3. **Monitor build**
   ```bash
   gcloud builds log <BUILD_ID> --stream
   ```

4. **View deployed image**
   ```bash
   gcloud container images list
   ```

### Option 2: Manual Docker Build & Push

1. **Build locally**
   ```bash
   docker build -t uipath-to-python:latest .
   ```

2. **Tag for GCP**
   ```bash
   docker tag uipath-to-python:latest gcr.io/YOUR_PROJECT_ID/uipath-to-python:latest
   ```

3. **Push to Container Registry**
   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/uipath-to-python:latest
   ```

4. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy uipath-to-python \
     --image gcr.io/YOUR_PROJECT_ID/uipath-to-python:latest \
     --region us-central1 \
     --memory 2Gi \
     --timeout 3600
   ```

## Run in Cloud

### Via Cloud Run (Serverless)
```bash
gcloud run invoke uipath-to-python --region us-central1
```

### Via Cloud Scheduler (Scheduled)
```bash
gcloud scheduler jobs create http image-downloader \
  --schedule="0 2 * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL" \
  --http-method=POST
```

### Via Compute Engine (VM)
```bash
gcloud compute instances create-with-container uipath-instance \
  --container-image=gcr.io/YOUR_PROJECT_ID/uipath-to-python:latest
```

## Environment Variables

Set secrets in GCP Secrets Manager:
```bash
echo -n "your-shared-drive-path" | gcloud secrets create SHARED_DRIVE_PATH --data-file=-
```

Reference in Cloud Run:
```bash
gcloud run deploy uipath-to-python \
  --set-secrets SHARED_DRIVE_PATH=SHARED_DRIVE_PATH:latest
```

## Troubleshooting

- **Browser issues**: Ensure Playwright browsers are cached in Docker
- **Timeout errors**: Increase timeout in cloudbuild.yaml or Cloud Run
- **Memory issues**: Increase memory allocation (default 256Mi, set to 2Gi or more)

## Clean Up

```bash
# Delete container image
gcloud container images delete gcr.io/YOUR_PROJECT_ID/uipath-to-python:latest

# Delete Cloud Run service
gcloud run services delete uipath-to-python --region us-central1

# Delete Cloud Build history
gcloud builds delete BUILD_ID
```
