FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/metamask-docs && \
    cd /workspace/metamask-docs && \
    git remote add origin https://github.com/MetaMask/metamask-docs.git && \
    git fetch --depth=1 origin 5bc38bd7ae8ef430aa0e55fb1a87f9981d47e44f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/metamask-docs
