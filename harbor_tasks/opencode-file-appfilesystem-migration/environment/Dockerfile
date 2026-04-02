FROM node:22-slim

# System deps
RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential python3 unzip tmux \
  && rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Clone repo at base commit (before the fix)
ARG REPO=https://github.com/anomalyco/opencode.git
ARG COMMIT=608607256716d953bdaaa3142efe6cc99da6baf0

RUN git clone --filter=blob:none "$REPO" /workspace/opencode \
  && cd /workspace/opencode \
  && git checkout "$COMMIT" \
  && git config user.email "agent@test" \
  && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

# Install deps (monorepo — install from root)
RUN bun install --frozen-lockfile || bun install

# Pre-compile TypeScript so typecheck is faster during eval
RUN cd packages/opencode && bun run typecheck || true

ENV PYTHONPATH="/workspace/opencode"