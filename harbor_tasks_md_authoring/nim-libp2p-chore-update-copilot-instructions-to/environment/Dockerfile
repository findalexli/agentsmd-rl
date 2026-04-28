FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nim-libp2p && \
    cd /workspace/nim-libp2p && \
    git remote add origin https://github.com/vacp2p/nim-libp2p.git && \
    git fetch --depth=1 origin 01c9de6e3aa2f7e1c3f7c616e7624e6cf8445a8f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nim-libp2p
