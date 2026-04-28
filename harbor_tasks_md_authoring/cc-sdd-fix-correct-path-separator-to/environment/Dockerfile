FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cc-sdd && \
    cd /workspace/cc-sdd && \
    git remote add origin https://github.com/gotalab/cc-sdd.git && \
    git fetch --depth=1 origin dcbd81d0178ad43ffe271e5b56e9d9121a154de9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cc-sdd
