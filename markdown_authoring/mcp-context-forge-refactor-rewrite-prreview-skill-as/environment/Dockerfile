FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mcp-context-forge && \
    cd /workspace/mcp-context-forge && \
    git remote add origin https://github.com/IBM/mcp-context-forge.git && \
    git fetch --depth=1 origin a5cf86fcf67be8342565fd92e1fa1923859b4b92 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mcp-context-forge
