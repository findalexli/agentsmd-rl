FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/humanlayer && \
    cd /workspace/humanlayer && \
    git remote add origin https://github.com/humanlayer/humanlayer.git && \
    git fetch --depth=1 origin 3d0ed95d939857af0f7ac8cceddee57ee5dd211e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/humanlayer
