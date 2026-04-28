FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mcp-server-tree-sitter && \
    cd /workspace/mcp-server-tree-sitter && \
    git remote add origin https://github.com/wrale/mcp-server-tree-sitter.git && \
    git fetch --depth=1 origin c1dc7209114c6eb05ef20d7dba61d88ddd689da8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mcp-server-tree-sitter
