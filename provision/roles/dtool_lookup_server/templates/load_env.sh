#!/bin/bash

#export JWT_PRIVATE_KEY_FILE=/home/dtool/id_rsa
#export JWT_PUBLIC_KEY_FILE=/home/dtool/id_rsa.pub
export JWT_PUBLIC_KEY="{{ JWT_PUBLIC_KEY }}"
export SQLALCHEMY_DATABASE_URI=sqlite:////home/dtool/app.db
export FLASK_APP="dserver:create_app()"
