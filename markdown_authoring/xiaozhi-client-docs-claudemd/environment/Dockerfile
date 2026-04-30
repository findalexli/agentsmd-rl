FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/xiaozhi-client && \
    cd /workspace/xiaozhi-client && \
    git remote add origin https://github.com/shenjingnan/xiaozhi-client.git && \
    git fetch --depth=1 origin d039e367c7dcee4d87eb5724525b207c26187a4a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/xiaozhi-client
