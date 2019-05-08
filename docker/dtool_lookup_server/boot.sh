#!/bin/sh
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - "dtool_lookup_server:create_app()"
