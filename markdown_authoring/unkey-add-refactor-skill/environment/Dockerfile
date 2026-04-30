FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/unkey && \
    cd /workspace/unkey && \
    git remote add origin https://github.com/unkeyed/unkey.git && \
    git fetch --depth=1 origin 81123bf1e14685cc0b25cc03fbe7d1a9f5d0a8ca && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/unkey
