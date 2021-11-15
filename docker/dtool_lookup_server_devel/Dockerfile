FROM python:3.10-bullseye

RUN adduser --disabled-password --gecos '' dtool_lookup_server

RUN pip install -U pip  && \
    pip install gunicorn  && \
    pip install 'flask<2.0' pymongo alembic flask-sqlalchemy flask-migrate flask-pymongo flask-cors \
        'dtoolcore>=3.18.0' dtool-cli dtool-info dtool-create dtool-s3 'flask-jwt-extended[asymmetric_crypto]>=4.0' \
        pyyaml psycopg2 && \
    rm -rf /root/.cache/pip

ENV FLASK_APP=dtool_lookup_server

COPY --chown=dtool_lookup_server . /app
RUN rm -Rf app/venv app/.idea app/.pytest_cache app/.git app/__pycache__

COPY docker/dtool_lookup_server_devel/dtool.json /home/dtool_lookup_server/.config/dtool/

WORKDIR /app

COPY docker/dtool_lookup_server_devel/boot.sh /
RUN chmod +x /boot.sh

RUN mkdir /keys && chown dtool_lookup_server /keys

USER dtool_lookup_server
EXPOSE 5000
ENTRYPOINT ["/boot.sh"]
