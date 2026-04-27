FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openclaw-codex-app-server && \
    cd /workspace/openclaw-codex-app-server && \
    git remote add origin https://github.com/pwrdrvr/openclaw-codex-app-server.git && \
    git fetch --depth=1 origin 4589fc8502176ffdc7679274dbfed0b9b894dc8e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw-codex-app-server
