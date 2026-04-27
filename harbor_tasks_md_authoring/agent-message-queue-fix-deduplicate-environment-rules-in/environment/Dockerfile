FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agent-message-queue && \
    cd /workspace/agent-message-queue && \
    git remote add origin https://github.com/avivsinai/agent-message-queue.git && \
    git fetch --depth=1 origin 23883014be11c835c628b433692822d8384eb3c4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-message-queue
