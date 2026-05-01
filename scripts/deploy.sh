#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
set -a
# shellcheck disable=SC1091
source .env
set +a

gcloud config set project "$GCP_ID"
gcloud auth application-default set-quota-project "$GCP_ID"

gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --port "$PORT" \
  --allow-unauthenticated \
  --add-cloudsql-instances "${GCP_ID}:${REGION}:${INSTANCE}" \
  --set-secrets "SECRET_KEY=SECRET_KEY:latest,SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI:latest" \
  --set-env-vars "FLASK_APP=app.py,PERMANENT_SESSION_LIFETIME=31536000,SQLALCHEMY_TRACK_MODIFICATIONS=False"
