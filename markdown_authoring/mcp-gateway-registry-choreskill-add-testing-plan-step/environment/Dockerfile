FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mcp-gateway-registry && \
    cd /workspace/mcp-gateway-registry && \
    git remote add origin https://github.com/agentic-community/mcp-gateway-registry.git && \
    git fetch --depth=1 origin 5a3cb07dfe7b4f76294637a3ee388ff08f2d80f9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mcp-gateway-registry
