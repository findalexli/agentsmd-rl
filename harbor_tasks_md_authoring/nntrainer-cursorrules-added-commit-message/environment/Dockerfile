FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nntrainer && \
    cd /workspace/nntrainer && \
    git remote add origin https://github.com/nntrainer/nntrainer.git && \
    git fetch --depth=1 origin 0e50be090a31c803a8c9f98f0859e206b85fff82 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nntrainer
