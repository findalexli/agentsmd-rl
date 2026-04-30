FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ruby-lsp && \
    cd /workspace/ruby-lsp && \
    git remote add origin https://github.com/Shopify/ruby-lsp.git && \
    git fetch --depth=1 origin 31ed10a793e9136b16bb9efbac780ae2506c7c05 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ruby-lsp
