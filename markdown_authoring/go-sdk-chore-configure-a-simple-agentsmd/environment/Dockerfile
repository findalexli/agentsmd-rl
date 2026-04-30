FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/go-sdk && \
    cd /workspace/go-sdk && \
    git remote add origin https://github.com/modelcontextprotocol/go-sdk.git && \
    git fetch --depth=1 origin ac65640a6841112cb7c08c48f903a903942b6351 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/go-sdk
