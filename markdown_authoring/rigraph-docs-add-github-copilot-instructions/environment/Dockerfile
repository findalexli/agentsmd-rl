FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/rigraph && \
    cd /workspace/rigraph && \
    git remote add origin https://github.com/igraph/rigraph.git && \
    git fetch --depth=1 origin 7918d80e106f7f5bd41867ad0e87a0a4834c4c9c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/rigraph
