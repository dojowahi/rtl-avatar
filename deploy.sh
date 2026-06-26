#!/bin/bash
# Exit immediately if a command fails
set -e

# --- Error Handler ---
error_handler() {
  local exit_code=$?
  local line_num=$1
  echo ""
  echo "❌ ERROR: Deployment failed at line $line_num with exit code $exit_code"
  exit $exit_code
}
trap 'error_handler $LINENO' ERR

# Load variables from ecommerce/backend/.env, excluding GCP/Vertex overrides
ENV_VARS=""
if [ -f "ecommerce/backend/.env" ]; then
  echo "📄 Found backend/.env, parsing variables..."
  ENV_VARS=$(grep -v '^#' ecommerce/backend/.env | grep -v '^$' | grep -v 'GOOGLE_CLOUD_PROJECT=' | grep -v 'GOOGLE_CLOUD_LOCATION=' | grep -v 'VERTEX_PROJECT_ID=' | grep -v 'VERTEX_LOCATION=' | tr -d '\r' | paste -s -d "," -)
fi

echo "🚀 Deploying cymbal-avatar to Cloud Run..."
gcloud run deploy cymbal-avatar \
  --source . \
  --region us-central1 \
  --project gen-ai-4all \
  --allow-unauthenticated \
  --service-account genai-592@gen-ai-4all.iam.gserviceaccount.com \
  --impersonate-service-account genai-592@gen-ai-4all.iam.gserviceaccount.com \
  --min-instances 1 \
  --no-cpu-throttling \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=gen-ai-4all,GOOGLE_CLOUD_LOCATION=global,VERTEX_PROJECT_ID=gen-ai-4all,VERTEX_LOCATION=global${ENV_VARS:+,}${ENV_VARS}"

echo "🎉 Deployment completed successfully!"
