FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/aqua-registry && \
    cd /workspace/aqua-registry && \
    git remote add origin https://github.com/aquaproj/aqua-registry.git && \
    git fetch --depth=1 origin 42895a1c741dc2a0b5b29a2cc63af43a1d7db30f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/aqua-registry
