FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/js-recall && \
    cd /workspace/js-recall && \
    git remote add origin https://github.com/recallnet/js-recall.git && \
    git fetch --depth=1 origin de0e31cf6bd679aeecf394971a50c07d2dc81dcf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/js-recall
