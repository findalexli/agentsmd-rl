FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/flow-playground && \
    cd /workspace/flow-playground && \
    git remote add origin https://github.com/onflow/flow-playground.git && \
    git fetch --depth=1 origin 7131966c03a31ff66f6d3a9499ea7498464272dc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/flow-playground
