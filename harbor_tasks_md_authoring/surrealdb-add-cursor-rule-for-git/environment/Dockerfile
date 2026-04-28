FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/surrealdb && \
    cd /workspace/surrealdb && \
    git remote add origin https://github.com/surrealdb/surrealdb.git && \
    git fetch --depth=1 origin fd6f6e9b37921fa53ce2b29ee514636a09f5f3c3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/surrealdb
