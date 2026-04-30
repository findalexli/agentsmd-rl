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
    git fetch --depth=1 origin 835a0151c2d203ccb935662d94920cc4e539e2a5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/flashinfer
