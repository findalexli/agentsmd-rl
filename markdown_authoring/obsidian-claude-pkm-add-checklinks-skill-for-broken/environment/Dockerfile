FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/obsidian-claude-pkm && \
    cd /workspace/obsidian-claude-pkm && \
    git remote add origin https://github.com/ballred/obsidian-claude-pkm.git && \
    git fetch --depth=1 origin 9b3356301ea067118098146c0a15d36c4530cab6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/obsidian-claude-pkm
