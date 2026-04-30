FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/metamask-extension && \
    cd /workspace/metamask-extension && \
    git remote add origin https://github.com/MetaMask/metamask-extension.git && \
    git fetch --depth=1 origin b51ef743c5b5218b3ce1e7ccd4d8682242425fa2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/metamask-extension
