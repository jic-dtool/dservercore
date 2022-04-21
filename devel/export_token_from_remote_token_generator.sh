#!/usr/bin/env bash

TOKEN=$(curl --insecure -H "Content-Type: application/json"  \
  -X POST -d '{"username": "testuser", "password": "test_password" }'  \
  https://localhost:5001/token | jq -r '.token')
echo "Generated token '${TOKEN}'"
export TOKEN

HEADER="Authorization: Bearer $TOKEN"
export HEADER
