FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/flashinfer && \
    cd /workspace/flashinfer && \
    git remote add origin https://github.com/flashinfer-ai/flashinfer.git && \
    git fetch --depth=1 origin 454e7b25d0c21da176f0ef775e3de4a12d6c7118 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/flashinfer
