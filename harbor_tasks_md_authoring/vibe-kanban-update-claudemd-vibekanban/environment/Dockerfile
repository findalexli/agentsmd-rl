FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vibe-kanban && \
    cd /workspace/vibe-kanban && \
    git remote add origin https://github.com/BloopAI/vibe-kanban.git && \
    git fetch --depth=1 origin d0392e6d5ebe77c206fed6380948f3af8631fb39 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vibe-kanban
