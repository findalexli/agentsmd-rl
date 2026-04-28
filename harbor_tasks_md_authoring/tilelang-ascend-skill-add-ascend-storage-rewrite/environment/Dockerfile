FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tilelang-ascend && \
    cd /workspace/tilelang-ascend && \
    git remote add origin https://github.com/tile-ai/tilelang-ascend.git && \
    git fetch --depth=1 origin b0b64bf6affd284c2912a52e06cf10c57e02930e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tilelang-ascend
