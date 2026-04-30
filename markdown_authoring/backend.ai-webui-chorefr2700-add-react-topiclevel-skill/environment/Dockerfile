FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/backend.ai-webui && \
    cd /workspace/backend.ai-webui && \
    git remote add origin https://github.com/lablup/backend.ai-webui.git && \
    git fetch --depth=1 origin 7005b4bd68369ce93c946c57e6f280a0a3a648f6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/backend.ai-webui
