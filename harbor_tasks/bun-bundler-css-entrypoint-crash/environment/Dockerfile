FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip unzip && \
    rm -rf /var/lib/apt/lists/*

# Clone bun repo at the base commit (treeless clone for speed on large repos)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 7abe6c387d0746b26eeed7fe9175e14560840cbb && \
    git checkout FETCH_HEAD

WORKDIR /workspace/bun

RUN mkdir -p /logs/verifier

# Copy test and evaluation files