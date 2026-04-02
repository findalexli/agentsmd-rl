FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Partial clone (blob:none) — only fetches tree objects, blobs on demand
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 36f17caa987d130788b97a6e9d7c9aea7895b6ed

RUN python3 -m pip install --no-cache-dir --break-system-packages pytest pytest-json-ctrf

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun