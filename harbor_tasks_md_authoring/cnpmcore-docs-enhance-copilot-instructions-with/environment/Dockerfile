FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cnpmcore && \
    cd /workspace/cnpmcore && \
    git remote add origin https://github.com/cnpm/cnpmcore.git && \
    git fetch --depth=1 origin 2e51399db11c9d0f9bc2e69347b0d26463776a94 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cnpmcore
