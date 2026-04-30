FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun v1.3.11 (matches repo packageManager)
ENV BUN_VERSION=1.3.11
RUN curl -fsSL "https://github.com/oven-sh/bun/releases/download/bun-v${BUN_VERSION}/bun-linux-x64.zip" -o /tmp/bun.zip \
    && unzip -q /tmp/bun.zip -d /tmp/bun \
    && cp /tmp/bun/bun-linux-x64/bun /usr/local/bin/bun \
    && chmod +x /usr/local/bin/bun \
    && rm -rf /tmp/bun /tmp/bun.zip \
    && bun --version

# Clone repo at base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin 9f94bdb49634bda90a2804585b8d739228dde876 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential commits
RUN git config user.email "agent@test" && git config user.name "Agent"

# Install dependencies and commit any lockfile changes from platform diff
RUN bun install && \
    git add -A && \
    git commit -m "chore: install dependencies" || true

ENV PYTHONPATH=/repo
