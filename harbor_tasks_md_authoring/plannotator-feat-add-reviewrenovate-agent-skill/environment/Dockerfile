FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/plannotator && \
    cd /workspace/plannotator && \
    git remote add origin https://github.com/backnotprop/plannotator.git && \
    git fetch --depth=1 origin 5c5527c9ae38d044cc4afc476376dfdb16f254fb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/plannotator
