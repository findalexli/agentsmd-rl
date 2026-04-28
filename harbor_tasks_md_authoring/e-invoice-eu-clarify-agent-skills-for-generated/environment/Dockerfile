FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/e-invoice-eu && \
    cd /workspace/e-invoice-eu && \
    git remote add origin https://github.com/gflohr/e-invoice-eu.git && \
    git fetch --depth=1 origin f24186b67ef5425b347d59f88e67c2b2dd20b800 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/e-invoice-eu
