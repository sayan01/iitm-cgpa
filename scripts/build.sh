#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
set -a
# shellcheck disable=SC1091
source .env
set +a

REGION=asia-south1
IMAGE="${REGION}-docker.pkg.dev/${GCP_ID}/iitm-cgpa/app:latest"

gcloud builds submit --tag "$IMAGE"
