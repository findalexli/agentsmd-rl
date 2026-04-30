FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ouroboros && \
    cd /workspace/ouroboros && \
    git remote add origin https://github.com/Q00/ouroboros.git && \
    git fetch --depth=1 origin 4164f266b186872ad755ba2b2b70fabb37a90dab && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ouroboros
