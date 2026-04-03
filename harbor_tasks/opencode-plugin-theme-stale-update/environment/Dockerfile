FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun (needed for running tests and building)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Clone repo at the base commit (before the fix)
ARG BASE_COMMIT=3c32013eb122d794089e011d2ec7077395d6f1c4
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

# Install dependencies (needed for bun test and module resolution)
RUN bun install --frozen-lockfile || bun install