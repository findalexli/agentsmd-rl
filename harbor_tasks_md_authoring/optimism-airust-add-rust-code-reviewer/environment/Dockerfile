FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/optimism && \
    cd /workspace/optimism && \
    git remote add origin https://github.com/ethereum-optimism/optimism.git && \
    git fetch --depth=1 origin 7517f61949647c1e9a94efb88277cc8f6ef4ae34 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/optimism
