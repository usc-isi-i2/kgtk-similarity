# A dockerfile for running the kgtk-similarity
# python 3.9.7 is a KGTK requirement
# this comes with a debian version 11 (bullseye)
FROM python:3.9.7

# update the registry
RUN apt-get update

# install sqlite3 database
RUN apt-get install sqlite3 -y

RUN mkdir /src

COPY requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

COPY app_config.py /src/
COPY application.py /src/
COPY semantic_similarity/ /src/semantic_similarity
COPY app/ /src/app/

ARG FLASK_ENV=production
ENV FLASK_ENV=$FLASK_ENV

ARG KGTK_SIMILARITY_CONFIG=semantic_similarity/config_v2_docker.json
ENV KGTK_SIMILARITY_CONFIG=$KGTK_SIMILARITY_CONFIG

WORKDIR /src
