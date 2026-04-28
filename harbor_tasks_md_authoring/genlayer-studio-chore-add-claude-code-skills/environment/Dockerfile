FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/genlayer-studio && \
    cd /workspace/genlayer-studio && \
    git remote add origin https://github.com/genlayerlabs/genlayer-studio.git && \
    git fetch --depth=1 origin ed7e18844760833aa992643df7bb591e66048d6d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/genlayer-studio
