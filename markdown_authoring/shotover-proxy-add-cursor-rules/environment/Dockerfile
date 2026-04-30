FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/shotover-proxy && \
    cd /workspace/shotover-proxy && \
    git remote add origin https://github.com/shotover/shotover-proxy.git && \
    git fetch --depth=1 origin 773a6dbcd46eaac6e42bde6a14e3ecec46e0f4bb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/shotover-proxy
