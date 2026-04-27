FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lemonade && \
    cd /workspace/lemonade && \
    git remote add origin https://github.com/lemonade-sdk/lemonade.git && \
    git fetch --depth=1 origin e4f90848d2c0ab55626e20aa017d8d65001c0bc3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lemonade
