FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cockroach && \
    cd /workspace/cockroach && \
    git remote add origin https://github.com/cockroachdb/cockroach.git && \
    git fetch --depth=1 origin 808ecd4b7ad7edee4061a720a5e5e0d083c55e76 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cockroach
