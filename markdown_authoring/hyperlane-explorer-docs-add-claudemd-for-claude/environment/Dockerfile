FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hyperlane-explorer && \
    cd /workspace/hyperlane-explorer && \
    git remote add origin https://github.com/hyperlane-xyz/hyperlane-explorer.git && \
    git fetch --depth=1 origin 764e2940f5c953fad519f02985dd9355508e2160 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hyperlane-explorer
