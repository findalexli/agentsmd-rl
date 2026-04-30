FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ruby-sdk && \
    cd /workspace/ruby-sdk && \
    git remote add origin https://github.com/modelcontextprotocol/ruby-sdk.git && \
    git fetch --depth=1 origin 70384c8362bce2b460e352f019aef2e61df3b316 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ruby-sdk
