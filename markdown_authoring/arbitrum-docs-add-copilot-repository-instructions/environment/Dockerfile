FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/arbitrum-docs && \
    cd /workspace/arbitrum-docs && \
    git remote add origin https://github.com/OffchainLabs/arbitrum-docs.git && \
    git fetch --depth=1 origin 699fff6a071b4d0c885bc90d547556a2cffe6875 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/arbitrum-docs
