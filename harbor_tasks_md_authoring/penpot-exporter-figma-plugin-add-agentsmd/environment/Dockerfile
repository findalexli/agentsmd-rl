FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/penpot-exporter-figma-plugin && \
    cd /workspace/penpot-exporter-figma-plugin && \
    git remote add origin https://github.com/penpot/penpot-exporter-figma-plugin.git && \
    git fetch --depth=1 origin 32a1339383c5e39e34c62610bce9ef67446c20fe && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/penpot-exporter-figma-plugin
