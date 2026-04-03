FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin f6e14f9d73b46ab319b334c013094d867d4ef149 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/playwright

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
