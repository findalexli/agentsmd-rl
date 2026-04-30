FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/perfetto && \
    cd /workspace/perfetto && \
    git remote add origin https://github.com/google/perfetto.git && \
    git fetch --depth=1 origin c50494582ef5bc1d0071c31a4aaceb4ba68e9aaf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/perfetto
