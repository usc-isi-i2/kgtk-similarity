# A dockerfile for running the kgtk-similarity
# python 3.9.7 is a KGTK requirement
# this comes with a debian version 11 (bullseye)
FROM python:3.9.7

# Add graph-tool repository to the list of known apt sources
RUN echo "deb [ arch=amd64 ] https://downloads.skewed.de/apt bullseye main" >> /etc/apt/sources.list

# Fetch the public key in order to verify graph-tool
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key 612DEFB798507F25

# update the registry
RUN apt-get update

# install graph-tool library for kgtk
RUN apt-get install python3-graph-tool -y

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

ARG KGTK_SIMILARITY_CONFIG=semantic_similarity/config.json
ENV KGTK_SIMILARITY_CONFIG=$KGTK_SIMILARITY_CONFIG

WORKDIR /src
