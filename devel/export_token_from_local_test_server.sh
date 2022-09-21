#!/usr/bin/env bash
APPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script in $APPDIR"
source ${APPDIR}/env.rc

DTOOL_LOOKUP_SERVER_TOKEN=$(flask user token testuser)
echo "Generated token '${DTOOL_LOOKUP_SERVER_TOKEN}'"
export DTOOL_LOOKUP_SERVER_TOKEN

HEADER="Authorization: Bearer ${DTOOL_LOOKUP_SERVER_TOKEN}"
export HEADER
