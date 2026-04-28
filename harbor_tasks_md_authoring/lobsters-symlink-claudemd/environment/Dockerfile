FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lobsters && \
    cd /workspace/lobsters && \
    git remote add origin https://github.com/lobsters/lobsters.git && \
    git fetch --depth=1 origin 8c3337560f8a6d7d8d3dae87c2586a6ec6090f71 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lobsters
