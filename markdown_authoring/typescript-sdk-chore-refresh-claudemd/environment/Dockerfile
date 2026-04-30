FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/typescript-sdk && \
    cd /workspace/typescript-sdk && \
    git remote add origin https://github.com/modelcontextprotocol/typescript-sdk.git && \
    git fetch --depth=1 origin 4b5c25d5926007c649ad2809be80188aa9c86ec4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/typescript-sdk
