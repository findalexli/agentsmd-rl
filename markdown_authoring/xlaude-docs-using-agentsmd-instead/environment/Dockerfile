FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/xlaude && \
    cd /workspace/xlaude && \
    git remote add origin https://github.com/Xuanwo/xlaude.git && \
    git fetch --depth=1 origin ce16a804f1a75664cb9522ce257afe265c8eaeec && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/xlaude
