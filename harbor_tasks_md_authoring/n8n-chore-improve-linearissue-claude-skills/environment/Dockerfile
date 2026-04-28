FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/n8n && \
    cd /workspace/n8n && \
    git remote add origin https://github.com/n8n-io/n8n.git && \
    git fetch --depth=1 origin 4c3dc92c5280bbfa016df4c562b9fe32aaec121d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/n8n
