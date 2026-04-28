FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/topograph && \
    cd /workspace/topograph && \
    git remote add origin https://github.com/NVIDIA/topograph.git && \
    git fetch --depth=1 origin 1875ab883fc20c5a993e25d5a9c3cb0ba2a22c71 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/topograph
