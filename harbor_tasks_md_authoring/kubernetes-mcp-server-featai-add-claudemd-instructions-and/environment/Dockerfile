FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/kubernetes-mcp-server && \
    cd /workspace/kubernetes-mcp-server && \
    git remote add origin https://github.com/containers/kubernetes-mcp-server.git && \
    git fetch --depth=1 origin aab94419e349cb20017a4a2c7ef03a93a3394a39 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/kubernetes-mcp-server
