FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vscode-reborn-ai && \
    cd /workspace/vscode-reborn-ai && \
    git remote add origin https://github.com/vscode-reborn-ai/vscode-reborn-ai.git && \
    git fetch --depth=1 origin 1335fa1a8398f3805d1664aa0d8a70a7096b0261 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode-reborn-ai
