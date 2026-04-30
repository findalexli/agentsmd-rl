FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/prometheus && \
    cd /workspace/prometheus && \
    git remote add origin https://github.com/prometheus/prometheus.git && \
    git fetch --depth=1 origin 24a057bbf9089677b4c49eac4ae1f28287ac8bb9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prometheus
