FROM python:3.10-bullseye

RUN adduser --disabled-password --gecos '' dserver

COPY --chown=dserver . /app

WORKDIR /app

ENV FLASK_APP=dserver

RUN pip install -U pip  && \
    pip install gunicorn  psycopg2 setuptools_scm && \
    pip install -r requirements.txt && \
    pip install dtool-cli dtool-info dtool-create dtool-s3 && \
    pip install git+https://github.com/jotelha/dserver-retrieve-plugin-mongo.git@main && \
    pip install git+https://github.com/jotelha/dserver-search-plugin-mongo.git@main && \
    pip install git+https://github.com/livMatS/dserver-direct-mongo-plugin.git@main && \
    pip install git+https://github.com/livMatS/dserver-dependency-graph-plugin.git@main && \
    pip install git+https://github.com/livMatS/dserver-notification-plugin.git@main && \
    rm -rf /root/.cache/pip

COPY docker/dserver_devel/dtool.json /home/dserver/.config/dtool/

COPY docker/dserver_devel/boot.sh  /
RUN chmod +x /boot.sh

RUN mkdir /keys && chown dserver /keys

USER dserver
EXPOSE 5000
ENTRYPOINT ["/boot.sh"]
