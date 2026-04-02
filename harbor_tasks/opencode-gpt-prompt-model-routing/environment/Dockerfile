FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Clone repo at base commit (before fix)
ARG REPO_URL=https://github.com/anomalyco/opencode.git
ARG BASE_COMMIT=17e8f577d681db858c7a24db2c91d1b45b7b85c9

RUN git clone "$REPO_URL" /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout "$BASE_COMMIT" \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

# Install dependencies (needed for bun to resolve imports in tests)
RUN bun install --frozen-lockfile || bun install
