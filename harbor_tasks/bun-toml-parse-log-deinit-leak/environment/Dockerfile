FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Partial clone (blob:none) — only fetches tree objects, blobs on demand
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 36f17caa987d130788b97a6e9d7c9aea7895b6ed && \
    git checkout FETCH_HEAD

RUN python3 -m pip install --no-cache-dir --break-system-packages pytest pytest-json-ctrf

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun