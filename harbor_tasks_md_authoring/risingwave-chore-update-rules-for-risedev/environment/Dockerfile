FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/risingwave && \
    cd /workspace/risingwave && \
    git remote add origin https://github.com/risingwavelabs/risingwave.git && \
    git fetch --depth=1 origin 68b9683d8f045a5ae1f9178b90f7d6d0ce5b74c1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/risingwave
