#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}
REGION=${REGION:-europe-west1}
SERVICE=${SERVICE:-container-ocr}
SA_NAME=${SA_NAME:-container-ocr}

if [ -z "$PROJECT_ID" ]; then
  echo "Не вибрано проєкт. Виконайте: gcloud config set project <PROJECT_ID>"
  exit 1
fi
BUCKET=${BUCKET:-${PROJECT_ID}-container-scans}
SA="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
cd "$(dirname "$0")"

step() { printf '\n== %s\n' "$*"; }
# новий сервісний акаунт в IAM з'являється не одразу, тому повтори
retry() {
  local n=0
  until "$@" >/dev/null; do
    n=$((n + 1)); [ $n -ge 12 ] && return 1
    echo "   ...ще не готово, повтор через 10 с"; sleep 10
  done
}

echo "Проєкт: $PROJECT_ID ($PROJECT_NUMBER), регіон: $REGION"
gcloud config set project "$PROJECT_ID" >/dev/null

step "1/6 Вмикаю API: Vision, Cloud Run, Cloud Build, Artifact Registry, Firestore, Storage, IAM, Compute"
gcloud services enable vision.googleapis.com run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com firestore.googleapis.com storage.googleapis.com \
  iam.googleapis.com compute.googleapis.com

step "2/6 База Firestore (Native mode)"
if gcloud firestore databases describe --database="(default)" >/dev/null 2>&1; then
  echo "   вже існує"
else
  retry gcloud firestore databases create --database="(default)" --location="$REGION" --type=firestore-native
fi

step "3/6 Бакет Cloud Storage для фото: gs://$BUCKET"
if gcloud storage buckets describe "gs://$BUCKET" >/dev/null 2>&1; then
  echo "   вже існує"
else
  gcloud storage buckets create "gs://$BUCKET" --location="$REGION" --uniform-bucket-level-access
fi

step "4/6 Сервісний акаунт $SA і його ролі"
if gcloud iam service-accounts describe "$SA" >/dev/null 2>&1; then
  echo "   вже існує"
else
  gcloud iam service-accounts create "$SA_NAME" --display-name="Container OCR (Cloud Run)"
fi
for role in roles/datastore.user roles/serviceusage.serviceUsageConsumer; do
  retry gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA" --role="$role" --condition=None --quiet
  echo "   $role"
done
retry gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" \
  --member="serviceAccount:$SA" --role="roles/storage.objectAdmin"
echo "   roles/storage.objectAdmin на бакет"
# збірку з --source робить дефолтний compute sa, йому треба run.builder
retry gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/run.builder" --condition=None --quiet
echo "   roles/run.builder для збірки"

step "5/6 API-ключ сервісу"
if [ -s .api_key ]; then
  API_KEY=$(cat .api_key)
  echo "   використовую збережений у .api_key"
else
  API_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(18))')
  echo "$API_KEY" > .api_key
  echo "   створено і збережено в .api_key"
fi

step "6/6 Збірка і деплой у Cloud Run (2-4 хвилини)"
gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --service-account "$SA" \
  --allow-unauthenticated \
  --memory 1Gi --cpu 1 \
  --min-instances 0 --max-instances 2 --concurrency 4 --timeout 60 \
  --set-env-vars "STORE=gcp,GCS_BUCKET=$BUCKET,API_KEY=$API_KEY" \
  --quiet

URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')
cat <<EOF

Готово.
  Сторінка:      $URL
  Документація:  $URL/docs
  API-ключ:      $API_KEY

Перевірка з терміналу:
  curl -s -H "X-API-Key: $API_KEY" -F file=@samples/door_valid.jpg "$URL/api/scan"
EOF
