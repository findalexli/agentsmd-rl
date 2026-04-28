FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lucid-agents && \
    cd /workspace/lucid-agents && \
    git remote add origin https://github.com/daydreamsai/lucid-agents.git && \
    git fetch --depth=1 origin 7d389978b4ef6f8fae56c073af5e6f4c53b636d8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lucid-agents
