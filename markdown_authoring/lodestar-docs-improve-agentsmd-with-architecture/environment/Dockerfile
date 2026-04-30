FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lodestar && \
    cd /workspace/lodestar && \
    git remote add origin https://github.com/ChainSafe/lodestar.git && \
    git fetch --depth=1 origin 2074a31ba7619fd6fae2d0d857af9c9ad530b998 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lodestar
