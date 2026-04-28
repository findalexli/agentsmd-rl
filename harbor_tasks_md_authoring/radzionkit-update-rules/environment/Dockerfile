FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/radzionkit && \
    cd /workspace/radzionkit && \
    git remote add origin https://github.com/radzionc/radzionkit.git && \
    git fetch --depth=1 origin 5c2f0652284b29a8a6e7a4037571c32cb3b6f676 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/radzionkit
