#!/bin/sh
if [ ! -d migrations ]; then
    echo "-> Initialize database..."
    flask db init
fi

echo "-> Migrating database..."
flask db migrate
flask db upgrade

echo "-> Register base URI..."
flask base_uri add s3://test-bucket

echo "-> Creating test user..."
flask user add test-user

echo "-> Setting permissions for test user..."
flask user search_permission test-user s3://test-bucket

echo "-> Index base URI..."
flask base_uri index s3://test-bucket
