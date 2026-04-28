FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/co-op-translator && \
    cd /workspace/co-op-translator && \
    git remote add origin https://github.com/Azure/co-op-translator.git && \
    git fetch --depth=1 origin ca81c2e6248420f63e3c36c26fd1649f4def3619 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/co-op-translator
