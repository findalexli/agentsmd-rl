FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cursor-memory-bank && \
    cd /workspace/cursor-memory-bank && \
    git remote add origin https://github.com/vanzan01/cursor-memory-bank.git && \
    git fetch --depth=1 origin a4190e501357a65044daf87e3e0e2ed886730e45 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cursor-memory-bank
