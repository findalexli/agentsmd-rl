FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hyperdx && \
    cd /workspace/hyperdx && \
    git remote add origin https://github.com/hyperdxio/hyperdx.git && \
    git fetch --depth=1 origin 45e8e1b62d7a1b56c78686a2233b8c5453ce9201 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hyperdx
