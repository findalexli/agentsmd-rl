FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/awesome-claude-md && \
    cd /workspace/awesome-claude-md && \
    git remote add origin https://github.com/sx4im/awesome-claude-md.git && \
    git fetch --depth=1 origin f8c5b5d1c111b480a11c24191cd716ee8f355ed3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/awesome-claude-md
