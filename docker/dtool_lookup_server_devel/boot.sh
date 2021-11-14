#!/bin/sh
echo "-> Listing dtool datasets"
dtool ls s3://test-bucket

echo "-> Upgrading database..."
flask db upgrade

echo "-> Starting gunicorn..."
exec gunicorn -b :5000 --access-logfile - --error-logfile - "dtool_lookup_server:create_app()"
