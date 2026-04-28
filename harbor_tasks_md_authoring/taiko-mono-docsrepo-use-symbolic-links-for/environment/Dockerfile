FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/taiko-mono && \
    cd /workspace/taiko-mono && \
    git remote add origin https://github.com/taikoxyz/taiko-mono.git && \
    git fetch --depth=1 origin 0cfd43cff6cf3bde4f61c30aeb9e7ccb17785a05 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/taiko-mono
