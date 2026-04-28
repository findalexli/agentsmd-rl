FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/shelf.nu && \
    cd /workspace/shelf.nu && \
    git remote add origin https://github.com/Shelf-nu/shelf.nu.git && \
    git fetch --depth=1 origin dbc16cfa91df219401d7474c3f1d5af731c82f49 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/shelf.nu
