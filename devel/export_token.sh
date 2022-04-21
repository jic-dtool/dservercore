#!/usr/bin/env bash
APPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script in $APPDIR"
source ${APPDIR}/env.rc

TOKEN=$(flask user token testuser)
echo "Generated token '${TOKEN}'"
export TOKEN

HEADER="Authorization: Bearer $TOKEN"
export HEADER
