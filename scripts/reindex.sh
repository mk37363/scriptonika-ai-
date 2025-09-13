#!/usr/bin/env bash
set -euo pipefail
API="https://app.scriptonika.ru"
EMAIL="marika@khlud.ru"
PASS="v1ExvE9IfD3g5vtT"

TOKEN=$(curl -sk -X POST "$API/api/admin/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" | jq -r .token)

curl -sk -X POST "$API/api/admin/reindex" \
  -H "Authorization: Bearer $TOKEN"
