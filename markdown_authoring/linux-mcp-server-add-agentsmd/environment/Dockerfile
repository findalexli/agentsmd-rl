FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/linux-mcp-server && \
    cd /workspace/linux-mcp-server && \
    git remote add origin https://github.com/rhel-lightspeed/linux-mcp-server.git && \
    git fetch --depth=1 origin aa02d78c35160725aad4271e292465b0e0be9d58 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/linux-mcp-server
