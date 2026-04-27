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
    git fetch --depth=1 origin cc14518d032f0f41bf9f789952fc5d5ec2a32fc1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/xiaohongshu-mcp
