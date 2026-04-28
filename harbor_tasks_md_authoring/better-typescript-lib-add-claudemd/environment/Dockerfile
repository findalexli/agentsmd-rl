FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/better-typescript-lib && \
    cd /workspace/better-typescript-lib && \
    git remote add origin https://github.com/uhyo/better-typescript-lib.git && \
    git fetch --depth=1 origin 6c01a89f73e0ee7d8116f676d073eac99052c3b1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/better-typescript-lib
