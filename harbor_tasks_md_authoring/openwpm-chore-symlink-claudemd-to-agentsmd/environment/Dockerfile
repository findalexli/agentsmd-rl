FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openwpm && \
    cd /workspace/openwpm && \
    git remote add origin https://github.com/openwpm/OpenWPM.git && \
    git fetch --depth=1 origin 253009bb00b83340ba2f3f49fc350ce9045eeb0c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openwpm
