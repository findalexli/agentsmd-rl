FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/zoneminder && \
    cd /workspace/zoneminder && \
    git remote add origin https://github.com/ZoneMinder/zoneminder.git && \
    git fetch --depth=1 origin cc8e84ff0b5aefd0d8b1d43cd1f71a9a97bcde21 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/zoneminder
