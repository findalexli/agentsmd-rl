FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/arcade-mcp && \
    cd /workspace/arcade-mcp && \
    git remote add origin https://github.com/ArcadeAI/arcade-mcp.git && \
    git fetch --depth=1 origin 317b9900baf079cdc78e5c0cfd05b01d0cd38263 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/arcade-mcp
