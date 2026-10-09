#!/usr/bin/env bash
# Видаляє все, що створив deploy.sh (після захисту лаби).
# База Firestore не видаляється: вона безкоштовна в межах free tier, а видалити її
# можна в консолі (Firestore -> Databases) або командою, яку скрипт надрукує наприкінці.
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

read -r -p "Видалити сервіс $SERVICE, бакет gs://$BUCKET і акаунт $SA у проєкті $PROJECT_ID? [y/N] " ok
[ "$ok" = "y" ] || [ "$ok" = "Y" ] || exit 0

gcloud run services delete "$SERVICE" --region "$REGION" --quiet || true
gcloud storage rm --recursive "gs://$BUCKET" --quiet || true
for role in roles/datastore.user roles/serviceusage.serviceUsageConsumer; do
  gcloud projects remove-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA" \
    --role="$role" --condition=None --quiet >/dev/null || true
done
gcloud iam service-accounts delete "$SA" --quiet || true
# бакет з вихідним кодом, який створює `gcloud run deploy --source`
gcloud storage rm --recursive "gs://run-sources-${PROJECT_ID}-${REGION}" --quiet 2>/dev/null || true
# образи, які зібрав Cloud Run, лежать в Artifact Registry
gcloud artifacts repositories delete cloud-run-source-deploy --location "$REGION" --quiet || true

echo
echo "Готово. Базу Firestore можна видалити так:"
echo "  gcloud firestore databases delete --database='(default)'"
