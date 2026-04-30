FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mcp-use && \
    cd /workspace/mcp-use && \
    git remote add origin https://github.com/mcp-use/mcp-use.git && \
    git fetch --depth=1 origin c7773455e67bbd69e35336f7068726cff88ee5a3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mcp-use
