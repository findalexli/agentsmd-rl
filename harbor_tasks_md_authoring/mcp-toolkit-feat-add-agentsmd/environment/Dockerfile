FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mcp-toolkit && \
    cd /workspace/mcp-toolkit && \
    git remote add origin https://github.com/nuxt-modules/mcp-toolkit.git && \
    git fetch --depth=1 origin 224b87f67c8a3ff4a681b25043498dfda297b533 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mcp-toolkit
