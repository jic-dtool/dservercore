#!/bin/bash

source load_env.sh
source /home/dtool/venv/bin/activate
exec gunicorn -D -b :5000 --access-logfile /home/dtool/logs/access.log --error-logfile /home/dtool/logs/error.log --pid /home/dtool/gunicorn.pid "dserver:create_app()"
