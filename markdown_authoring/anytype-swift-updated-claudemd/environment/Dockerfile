FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/anytype-swift && \
    cd /workspace/anytype-swift && \
    git remote add origin https://github.com/anyproto/anytype-swift.git && \
    git fetch --depth=1 origin c2e2389edbea03f496c8504e2531a62bbb383673 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/anytype-swift
