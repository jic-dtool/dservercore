#!/bin/bash -x
# run from repository root
ROOTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
APPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Repository in $ROOTDIR, Script in $APPDIR"
source ${APPDIR}/env.rc

openssl genrsa -out ${JWT_PRIVATE_KEY_FILE} 2048
openssl rsa -in ${JWT_PRIVATE_KEY_FILE} -pubout -outform PEM -out ${JWT_PUBLIC_KEY_FILE}

mkdir -p ${ROOTDIR}/data
docker run --user ${UID}:${UID} -d -p 27017:27017 -v ${ROOTDIR}/data:/data/db mongo:latest

flask db init
flask db migrate
flask db upgrade

flask base_uri add s3://test-bucket
flask base_uri add smb://test-share

flask base_uri index s3://test-bucket
flask base_uri index smb://test-share

flask user add testuser
flask user search_permission testuser s3://test-bucket
flask user register_permission testuser s3://test-bucket

flask run

# run after server is up
# flask user token testuser
