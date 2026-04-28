FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-relay-service && \
    cd /workspace/claude-relay-service && \
    git remote add origin https://github.com/Wei-Shaw/claude-relay-service.git && \
    git fetch --depth=1 origin b4658e5d5fbfc9085fea9135a1064ad095628829 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-relay-service
