FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

ARG REPO_URL=https://github.com/apache/superset.git
ARG BASE_COMMIT=01aa4d32816bdd9beffd0b22c53861145fcc42bb

WORKDIR /workspace
RUN git clone --filter=blob:none "${REPO_URL}" superset \
 && cd superset \
 && git checkout "${BASE_COMMIT}"

RUN pip install --no-cache-dir \
    sqlglot==28.10.0 \
    pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
