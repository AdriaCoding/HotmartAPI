#!/usr/bin/env bash
# GET /club/api/v1/users — Club API (see Postman: Club API / GET -club-api-v1-users)
#
# Requires:
#   HOTMART_ACCESS_TOKEN — Bearer token (same name as ./scripts/hotmart-request-token.sh prints).
#     When running this file as ./users.sh, the token must be exported: export HOTMART_ACCESS_TOKEN
#
set -euo pipefail

# Require OAuth token from the environment (same as hotmart-request-token.sh / "HOTMART_ACCESS_TOKEN is set").
: "${HOTMART_ACCESS_TOKEN:?set HOTMART_ACCESS_TOKEN}"

curl -sS "https://developers.hotmart.com/club/api/v1/users?subdomain=organic-ecom" \
  -H "Authorization: Bearer ${HOTMART_ACCESS_TOKEN}" \
  -H "Accept: application/json"
