FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pgdog && \
    cd /workspace/pgdog && \
    git remote add origin https://github.com/pgdogdev/pgdog.git && \
    git fetch --depth=1 origin f1d1dd50cfe46b8a85d58048243d4fcb81a78398 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pgdog
