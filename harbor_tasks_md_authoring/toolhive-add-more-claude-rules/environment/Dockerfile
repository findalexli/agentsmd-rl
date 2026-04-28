FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/toolhive && \
    cd /workspace/toolhive && \
    git remote add origin https://github.com/stacklok/toolhive.git && \
    git fetch --depth=1 origin 64378ce272a4cb2b0e8b3f96dc9eeeaec02d3381 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/toolhive
