FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-007-agents && \
    cd /workspace/claude-007-agents && \
    git remote add origin https://github.com/avivl/claude-007-agents.git && \
    git fetch --depth=1 origin fdf7bac393f4c1384080faec27980f04e2230838 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-007-agents
