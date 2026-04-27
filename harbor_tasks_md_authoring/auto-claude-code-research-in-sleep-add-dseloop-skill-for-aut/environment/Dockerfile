FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/auto-claude-code-research-in-sleep && \
    cd /workspace/auto-claude-code-research-in-sleep && \
    git remote add origin https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git && \
    git fetch --depth=1 origin 69039781115bf1364275ab2089b07a43b5ffedb6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/auto-claude-code-research-in-sleep
