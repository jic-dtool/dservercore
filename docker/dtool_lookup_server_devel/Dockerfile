FROM python:3.10-bullseye

RUN adduser --disabled-password --gecos '' dtool_lookup_server

COPY --chown=dtool_lookup_server . /app

WORKDIR /app

ENV FLASK_APP=dtool_lookup_server

RUN pip install -U pip  && \
    pip install gunicorn  psycopg2 setuptools_scm && \
    pip install -r requirements.txt && \
    pip install dtool-cli dtool-info dtool-create dtool-s3 && \
    pip install git+https://github.com/jotelha/dtool-lookup-server-retrieve-plugin-mongo.git@main && \
    pip install git+https://github.com/jotelha/dtool-lookup-server-search-plugin-mongo.git@main && \
    pip install git+https://github.com/livMatS/dtool-lookup-server-direct-mongo-plugin.git@main && \
    pip install git+https://github.com/livMatS/dtool-lookup-server-dependency-graph-plugin.git@main && \
    pip install git+https://github.com/livMatS/dtool-lookup-server-notification-plugin.git@main && \
    rm -rf /root/.cache/pip

COPY docker/dtool_lookup_server_devel/dtool.json /home/dtool_lookup_server/.config/dtool/

COPY docker/dtool_lookup_server_devel/boot.sh  /
RUN chmod +x /boot.sh

RUN mkdir /keys && chown dtool_lookup_server /keys

USER dtool_lookup_server
EXPOSE 5000
ENTRYPOINT ["/boot.sh"]
