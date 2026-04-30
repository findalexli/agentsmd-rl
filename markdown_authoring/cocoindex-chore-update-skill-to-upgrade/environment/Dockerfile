FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cocoindex && \
    cd /workspace/cocoindex && \
    git remote add origin https://github.com/cocoindex-io/cocoindex.git && \
    git fetch --depth=1 origin 35754cf29a2b696febcde0fa01d04d56f9e5ecde && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cocoindex
