FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/rust-payjoin && \
    cd /workspace/rust-payjoin && \
    git remote add origin https://github.com/payjoin/rust-payjoin.git && \
    git fetch --depth=1 origin 203c4a86d1d65a0fe9df22181a16f305b429c340 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/rust-payjoin
