FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cloudbase-mcp && \
    cd /workspace/cloudbase-mcp && \
    git remote add origin https://github.com/TencentCloudBase/CloudBase-MCP.git && \
    git fetch --depth=1 origin 87e7fc2600675aa754d2611953904b5328971f4a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cloudbase-mcp
