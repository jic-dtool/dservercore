FROM python:3.6-jessie

RUN adduser --disabled-password --gecos '' dtool_lookup_server

RUN pip install -U pip  && \
    pip install gunicorn  && \
    pip install dtool-lookup-server==0.6.0  && \
    rm -rf /root/.cache/pip

ENV FLASK_APP=dtool_lookup_server

WORKDIR /home/dtool_lookup_server

COPY boot.sh ./
RUN chmod +x boot.sh

RUN chown -R dtool_lookup_server:dtool_lookup_server ./

USER dtool_lookup_server
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
