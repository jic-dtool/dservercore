#!/bin/bash

source load_env.sh
exec gunicorn -D -b :5000 --access-logfile /home/dtool/logs/access.log --error-logfile /home/dtool/logs/error.log --pid /home/dtool/gunicorn.pid "dtool_lookup_server:create_app()"
