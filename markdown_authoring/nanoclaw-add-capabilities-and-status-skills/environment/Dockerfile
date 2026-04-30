FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nanoclaw && \
    cd /workspace/nanoclaw && \
    git remote add origin https://github.com/qwibitai/nanoclaw.git && \
    git fetch --depth=1 origin e7d0ffb208aef464ec5b30e9e3bfc0c7c87f4bb1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nanoclaw
