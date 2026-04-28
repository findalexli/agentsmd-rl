FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-code-game-studios && \
    cd /workspace/claude-code-game-studios && \
    git remote add origin https://github.com/Donchitos/Claude-Code-Game-Studios.git && \
    git fetch --depth=1 origin 666e0fcb5ad3f5f0f56e1219e8cf03d44e62a49a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-code-game-studios
