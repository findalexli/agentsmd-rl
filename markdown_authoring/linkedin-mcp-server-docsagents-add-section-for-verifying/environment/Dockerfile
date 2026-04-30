FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/linkedin-mcp-server && \
    cd /workspace/linkedin-mcp-server && \
    git remote add origin https://github.com/stickerdaniel/linkedin-mcp-server.git && \
    git fetch --depth=1 origin b2bc7e01c3697c1626df92145bbffe38b30a5b8d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/linkedin-mcp-server
