FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun (pinned version matching repo packageManager)
RUN curl -fsSL https://github.com/oven-sh/bun/releases/download/bun-v1.3.11/bun-linux-x64.zip -o /tmp/bun.zip && \
    unzip -q /tmp/bun.zip -d /tmp/bun-extract && \
    mv /tmp/bun-extract/bun-linux-x64/bun /usr/local/bin/bun && \
    chmod +x /usr/local/bin/bun && \
    rm -rf /tmp/bun.zip /tmp/bun-extract

# Clone repo at base commit (before the fix)
ARG BASE_COMMIT=5a6d10cd5363bd47c8e666bbc63435853a1f25b5
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

# Pre-install dependencies (bun install at repo root)
WORKDIR /workspace/opencode
RUN bun install --frozen-lockfile || bun install

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
