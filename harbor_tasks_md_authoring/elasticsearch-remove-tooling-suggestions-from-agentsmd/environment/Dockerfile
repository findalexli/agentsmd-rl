FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/elasticsearch && \
    cd /workspace/elasticsearch && \
    git remote add origin https://github.com/elastic/elasticsearch.git && \
    git fetch --depth=1 origin 9bb41868051ef9b21230af412c57dd1c2186f170 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/elasticsearch
