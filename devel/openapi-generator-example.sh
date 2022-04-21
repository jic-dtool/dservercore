#!/bin/bash
#
# Generate openapi python client from openapi description.
#
# Validate local description file:
#
#   docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli validate -i /local/openapi.json
#
# Validate openapi descrition provided by local lookup server:
#
#   docker run --rm --network="host" openapitools/openapi-generator-cli validate -i http://127.0.0.1:5000/doc/openapi.json
#
# Generate python API from local descritption file:
#
#     docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
#        -i /local/openapi.json \
#        -g python \
#        -o /local/out/python
#
# Generate python client api generator sample config file:
#
#     docker run --rm openapitools/openapi-generator-cli config-help -g python -f yamlsample > python-client-config.yml
#
# Generate python API from openapi descrition provided by local lookup server:
#
docker run --rm --network="host" -v "${PWD}:/local" --user $UID:$UID openapitools/openapi-generator-cli:latest generate \
    --package-name "dtool_lookup_openapi_client" \
    --git-user-id "jotelha" \
    --git-repo-id "dtool-lookup-openapi-client" \
    --release-note "auto-generated openapi client for dtool-lookup-server" \
    -c /local/python-client-config.yml \
    -i http://127.0.0.1:5000/doc/openapi.json \
    -o /local/out/python \
    -g python \
    --verbose

docker run --rm --network="host" -v "${PWD}:/local" --user $UID:$UID openapitools/openapi-generator-cli:latest generate \
    --package-name "dtool_lookup_openapi_client" \
    --git-user-id "jotelha" \
    --git-repo-id "dtool-lookup-openapi-python-legacy-client" \
    --release-note "auto-generated openapi client for dtool-lookup-server" \
    -c /local/python-legacy-client-config.yml \
    -i http://127.0.0.1:5000/doc/openapi.json \
    -o /local/out/python-legacy \
    -g python-legacy \
    --verbose
