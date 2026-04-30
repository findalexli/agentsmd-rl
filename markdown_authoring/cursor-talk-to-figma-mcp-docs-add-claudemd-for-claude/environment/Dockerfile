FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cursor-talk-to-figma-mcp && \
    cd /workspace/cursor-talk-to-figma-mcp && \
    git remote add origin https://github.com/grab/cursor-talk-to-figma-mcp.git && \
    git fetch --depth=1 origin dcd239a1f39142c99b21ba2ed07173f6ea764b77 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cursor-talk-to-figma-mcp
