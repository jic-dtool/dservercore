#!/usr/bin/env bash

DTOOL_LOOKUP_SERVER_TOKEN_GENERATOR_URL="${DTOOL_LOOKUP_SERVER_TOKEN_GENERATOR_URL:-https://localhost:5001/token}"

echo "Fetch token from ${DTOOL_LOOKUP_SERVER_TOKEN_GENERATOR_URL}."
DTOOL_LOOKUP_SERVER_TOKEN=$(curl --insecure -H "Content-Type: application/json"  \
  -X POST -d '{"username": "testuser", "password": "test_password" }'  \
  "${DTOOL_LOOKUP_SERVER_TOKEN_GENERATOR_URL}" | jq -r '.token')
echo "Generated token '${DTOOL_LOOKUP_SERVER_TOKEN}'"
export DTOOL_LOOKUP_SERVER_TOKEN

HEADER="Authorization: Bearer ${DTOOL_LOOKUP_SERVER_TOKEN}"
export HEADER
