FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/compound-engineering-plugin && \
    cd /workspace/compound-engineering-plugin && \
    git remote add origin https://github.com/EveryInc/compound-engineering-plugin.git && \
    git fetch --depth=1 origin 88e7a5250fff7a274b595831fc91583d46bdc585 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/compound-engineering-plugin
