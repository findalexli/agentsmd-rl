FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cargo-crev && \
    cd /workspace/cargo-crev && \
    git remote add origin https://github.com/crev-dev/cargo-crev.git && \
    git fetch --depth=1 origin 59528b8a0f91ae894a8b965240510f8de0ff2285 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cargo-crev
