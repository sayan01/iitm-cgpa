#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
set -a
# shellcheck disable=SC1091
source .env
set +a

gcloud config set project "$GCP_ID"
gcloud auth application-default set-quota-project "$GCP_ID"

gcloud builds submit --tag "$IMAGE"
