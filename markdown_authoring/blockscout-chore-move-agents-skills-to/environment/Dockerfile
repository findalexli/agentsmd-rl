FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/blockscout && \
    cd /workspace/blockscout && \
    git remote add origin https://github.com/blockscout/blockscout.git && \
    git fetch --depth=1 origin 304b892f7b15256cebcde6b75b639801a2e424ff && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/blockscout
