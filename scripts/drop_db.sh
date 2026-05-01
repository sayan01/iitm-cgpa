#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
set -a
# shellcheck disable=SC1091
source .env
set +a

echo -n "This drops the CloudSQL Database of $GCP_ID. Are you sure? (y/N) "
read -r response
if [[ "$response" != "y" ]]; then
  echo "Aborting."
  exit 0
fi

gcloud config set project "$GCP_ID"
gcloud auth application-default set-quota-project "$GCP_ID"

cloud-sql-proxy "$GCP_ID:$REGION:$INSTANCE" &
pid=$!
trap "kill $pid" EXIT
sleep 1
export PGPASSWORD="$DB_PASSWORD"

psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_NAME" \
  -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'

kill $pid