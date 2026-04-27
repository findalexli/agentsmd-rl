FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/xiaohongshu-mcp && \
    cd /workspace/xiaohongshu-mcp && \
    git remote add origin https://github.com/xpzouying/xiaohongshu-mcp.git && \
    git fetch --depth=1 origin 3b543c79babed5862d2478011fa365805d260b2b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/xiaohongshu-mcp
