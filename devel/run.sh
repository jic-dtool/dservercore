#!/bin/sh
echo "$(pwd)"
echo "-> Starting gunicorn..."
gunicorn -b :5000 --access-logfile - --error-logfile - --log-level ${LOGLEVEL} wsgi:app
