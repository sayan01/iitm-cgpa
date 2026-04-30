#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
set -a
# shellcheck disable=SC1091
source .env
set +a

REGION=asia-south1
SERVICE=iitm-cgpa
INSTANCE=iitm-cgpa-db
IMAGE="${REGION}-docker.pkg.dev/${GCP_ID}/iitm-cgpa/app:latest"

gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --port "$PORT" \
  --allow-unauthenticated \
  --add-cloudsql-instances "${GCP_ID}:${REGION}:${INSTANCE}" \
  --set-secrets "SECRET_KEY=SECRET_KEY:latest,SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI:latest" \
  --set-env-vars "FLASK_APP=app.py,PERMANENT_SESSION_LIFETIME=31536000,SQLALCHEMY_TRACK_MODIFICATIONS=False"
