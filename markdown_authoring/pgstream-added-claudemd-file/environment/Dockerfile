FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pgstream && \
    cd /workspace/pgstream && \
    git remote add origin https://github.com/xataio/pgstream.git && \
    git fetch --depth=1 origin f2e63d8a5a0178b7975f0ceb4d26e2b5e58bb6e9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pgstream
