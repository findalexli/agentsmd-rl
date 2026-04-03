FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin f736116967f5b57d89978e51961f2e78eedb443b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

# Install dependencies at current versions (beta.37)
RUN bun install --frozen-lockfile || bun install

# Configure git for any patching
RUN git config user.email "test@test.com" && git config user.name "Test"

ENV PYTHONPATH=/workspace/opencode