FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-codex-settings && \
    cd /workspace/claude-codex-settings && \
    git remote add origin https://github.com/fcakyon/claude-codex-settings.git && \
    git fetch --depth=1 origin f24d55df795738ac7c44a3a05ebdd62289893778 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-codex-settings
