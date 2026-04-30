FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/exram.gremlinq && \
    cd /workspace/exram.gremlinq && \
    git remote add origin https://github.com/Gremlinq/ExRam.Gremlinq.git && \
    git fetch --depth=1 origin d2233721a893b3bac3c5531e3dd5a4c7b02b8a90 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/exram.gremlinq
