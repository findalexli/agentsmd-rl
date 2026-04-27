FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/chrome-devtools-mcp && \
    cd /workspace/chrome-devtools-mcp && \
    git remote add origin https://github.com/ChromeDevTools/chrome-devtools-mcp.git && \
    git fetch --depth=1 origin 5dc00b3005bc945a9140195d0321bce2ed98de90 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/chrome-devtools-mcp
