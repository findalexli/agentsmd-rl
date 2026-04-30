FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/csharp-sdk && \
    cd /workspace/csharp-sdk && \
    git remote add origin https://github.com/modelcontextprotocol/csharp-sdk.git && \
    git fetch --depth=1 origin 89fcf3f8b7db80bb7de6fcf7c8091b362fb18f84 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/csharp-sdk
