FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/eslint-interactive && \
    cd /workspace/eslint-interactive && \
    git remote add origin https://github.com/mizdra/eslint-interactive.git && \
    git fetch --depth=1 origin ab6cd05f1eb915326ca31606253ea1ec8a27fd07 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/eslint-interactive
