#!/bin/bash
# Usage: ./get_token.sh <username> <token_server>

USERNAME=$1
TOKEN_SERVER=$2
CURL_OPTS=${@:3}

if [ -z "$USERNAME" ]
then
    echo "Please specify the username"
    exit 1
fi

if [ -z "$TOKEN_SERVER" ]
then
    echo "Please specify the token server"
    exit 1
fi

read -s -p "Password: " PASSWORD
echo ""

TOKEN=$(curl $CURL_OPTS -H "Content-Type: application/json"  -X POST -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\" }"  $TOKEN_SERVER/token | cut -d\" -f8)

if [ -z "$TOKEN" ]
then
    echo "Incorrect password"
    exit 1
fi

echo $TOKEN
