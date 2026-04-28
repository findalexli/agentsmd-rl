FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/llphant && \
    cd /workspace/llphant && \
    git remote add origin https://github.com/LLPhant/LLPhant.git && \
    git fetch --depth=1 origin a538b04bcfa4b907ec387d39a98d8323a73c2502 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/llphant
