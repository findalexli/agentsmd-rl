FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openapi-diff && \
    cd /workspace/openapi-diff && \
    git remote add origin https://github.com/Azure/openapi-diff.git && \
    git fetch --depth=1 origin 2d7d4da21eefc6de65548c5aa1d3261471e6658d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openapi-diff
