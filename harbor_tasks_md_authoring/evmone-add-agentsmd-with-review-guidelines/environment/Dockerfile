FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/evmone && \
    cd /workspace/evmone && \
    git remote add origin https://github.com/ipsilon/evmone.git && \
    git fetch --depth=1 origin c7d54ae0d9a33c55c224e5190b3debd2dc0ef96a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/evmone
