FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-command-suite && \
    cd /workspace/claude-command-suite && \
    git remote add origin https://github.com/qdhenry/Claude-Command-Suite.git && \
    git fetch --depth=1 origin f6ef4c887babf46036eadc0ac87a08f8ad639fa0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-command-suite
