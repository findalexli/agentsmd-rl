FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tea-tasting && \
    cd /workspace/tea-tasting && \
    git remote add origin https://github.com/e10v/tea-tasting.git && \
    git fetch --depth=1 origin f0bf6724c8d4c8c2d0c80e585982340c437c9f5c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tea-tasting
