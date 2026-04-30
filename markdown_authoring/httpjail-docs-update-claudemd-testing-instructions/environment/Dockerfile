FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/httpjail && \
    cd /workspace/httpjail && \
    git remote add origin https://github.com/coder/httpjail.git && \
    git fetch --depth=1 origin f5fb78f08a8503c0c4fba1dead7366601fb700b5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/httpjail
