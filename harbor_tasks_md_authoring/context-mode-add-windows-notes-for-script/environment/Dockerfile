FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/context-mode && \
    cd /workspace/context-mode && \
    git remote add origin https://github.com/mksglu/context-mode.git && \
    git fetch --depth=1 origin 45a8ffcb1f81159c6c6b61c594507504ac0b2333 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/context-mode
