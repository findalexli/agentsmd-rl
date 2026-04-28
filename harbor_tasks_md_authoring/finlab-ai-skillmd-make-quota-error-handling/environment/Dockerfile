FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/finlab-ai && \
    cd /workspace/finlab-ai && \
    git remote add origin https://github.com/koreal6803/finlab-ai.git && \
    git fetch --depth=1 origin f7ef356f8f4f660aafb2320747c0ddb5956ce0db && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/finlab-ai
