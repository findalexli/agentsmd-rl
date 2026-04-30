FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nanostack && \
    cd /workspace/nanostack && \
    git remote add origin https://github.com/garagon/nanostack.git && \
    git fetch --depth=1 origin d7b36c70d2cb2a4ae1e1349968f7f569bd280acf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nanostack
