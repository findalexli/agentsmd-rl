FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/saleor && \
    cd /workspace/saleor && \
    git remote add origin https://github.com/saleor/saleor.git && \
    git fetch --depth=1 origin 94ea1418175967f4c1bf0c8731a1008bf9c6f1bf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/saleor
