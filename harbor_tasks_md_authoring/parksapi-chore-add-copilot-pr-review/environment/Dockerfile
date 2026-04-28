FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/parksapi && \
    cd /workspace/parksapi && \
    git remote add origin https://github.com/ThemeParks/parksapi.git && \
    git fetch --depth=1 origin b9a6e4ecf346205224fa42918b64e295d43521dc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/parksapi
