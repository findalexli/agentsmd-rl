FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/spotlight && \
    cd /workspace/spotlight && \
    git remote add origin https://github.com/getsentry/spotlight.git && \
    git fetch --depth=1 origin 7287f4b641c26405c6c3c6b361b0ab63998940db && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/spotlight
