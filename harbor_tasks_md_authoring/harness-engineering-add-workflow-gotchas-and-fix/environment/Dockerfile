FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/harness-engineering && \
    cd /workspace/harness-engineering && \
    git remote add origin https://github.com/jrenaldi79/harness-engineering.git && \
    git fetch --depth=1 origin d5e92135683ff253c68f1eb2e6b3965fd5e528c6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/harness-engineering
