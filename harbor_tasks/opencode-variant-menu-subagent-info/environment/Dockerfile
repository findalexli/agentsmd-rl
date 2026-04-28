FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip python3-venv unzip \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test User"

# Install bun from pinned GitHub release (no curl | bash)
ARG BUN_VERSION=1.3.13
RUN curl -fsSL "https://github.com/oven-sh/bun/releases/download/bun-v${BUN_VERSION}/bun-linux-x64.zip" -o /tmp/bun.zip && \
    cd /tmp && unzip -o bun.zip && \
    cp bun-linux-x64/bun /usr/local/bin/bun 2>/dev/null || cp bun /usr/local/bin/bun && \
    chmod +x /usr/local/bin/bun && rm -rf /tmp/bun*

# Clone repo at base commit (before the fix)
ARG BASE_COMMIT=860531c275cf845f80ccf26bba5bad745fe98398
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

# Pre-install dependencies so tests don't need to download/install bun
RUN cd /workspace/opencode && bun install

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
