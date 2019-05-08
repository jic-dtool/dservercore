#!/bin/bash

export JWT_PRIVATE_KEY_FILE=/home/dtool/id_rsa
export JWT_PUBLIC_KEY_FILE=/home/dtool/id_rsa.pub
export SQLALCHEMY_DATABASE_URI=sqlite:////home/dtool/app.db
export FLASK_APP="dtool_lookup_server:create_app()"
