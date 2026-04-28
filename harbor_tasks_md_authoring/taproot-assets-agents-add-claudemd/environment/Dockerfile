FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/taproot-assets && \
    cd /workspace/taproot-assets && \
    git remote add origin https://github.com/lightninglabs/taproot-assets.git && \
    git fetch --depth=1 origin f3b15dcbf49403d62dd3ed87527163e2c13165e3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/taproot-assets
