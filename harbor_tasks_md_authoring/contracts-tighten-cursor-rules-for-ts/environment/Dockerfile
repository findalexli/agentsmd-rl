FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/contracts && \
    cd /workspace/contracts && \
    git remote add origin https://github.com/lifinance/contracts.git && \
    git fetch --depth=1 origin 410d6bb45bc5d80a99e9f5a0d978e5d99c970251 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/contracts
