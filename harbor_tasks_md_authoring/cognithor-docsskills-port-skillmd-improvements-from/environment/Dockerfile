FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cognithor && \
    cd /workspace/cognithor && \
    git remote add origin https://github.com/Alex8791-cyber/cognithor.git && \
    git fetch --depth=1 origin 1af17e0cc2175ee643d6027887f18e410c87da0b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cognithor
