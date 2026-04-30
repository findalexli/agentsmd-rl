FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/octocode-mcp && \
    cd /workspace/octocode-mcp && \
    git remote add origin https://github.com/bgauryy/octocode-mcp.git && \
    git fetch --depth=1 origin 2709273d2c0fd0e0830acc28f012169acd372438 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/octocode-mcp
