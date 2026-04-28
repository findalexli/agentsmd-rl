FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sovereign-sdk && \
    cd /workspace/sovereign-sdk && \
    git remote add origin https://github.com/Sovereign-Labs/sovereign-sdk.git && \
    git fetch --depth=1 origin 7b5d03ac54b4df6dda311f39f42574de0d84bf64 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sovereign-sdk
