FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/unity-mcp && \
    cd /workspace/unity-mcp && \
    git remote add origin https://github.com/IvanMurzak/Unity-MCP.git && \
    git fetch --depth=1 origin 9e0b9afde9489caf07657ecd4dc647cc5c979568 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/unity-mcp
