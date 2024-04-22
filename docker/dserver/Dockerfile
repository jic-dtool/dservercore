FROM python:3.10-bullseye

RUN adduser --disabled-password --gecos '' dserver

RUN pip install -U pip  && \
    pip install gunicorn  && \
    pip install dserver==0.6.0  && \
    rm -rf /root/.cache/pip

ENV FLASK_APP=dtool_lookup_server

WORKDIR /home/dserver

COPY boot.sh ./
RUN chmod +x boot.sh

RUN chown -R dserver:dserver ./

USER dserver
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
