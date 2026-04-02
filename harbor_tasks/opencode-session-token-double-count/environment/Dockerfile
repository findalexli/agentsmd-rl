FROM oven/bun:1.2-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git clone https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout 5c15755a10fecf15630232c478302a766d295012

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

# Configure git for agent use
RUN git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install dependencies
RUN bun install --frozen-lockfile || bun install

# Precompile TypeScript to catch issues early
RUN cd packages/opencode && bun run typecheck || true

ENV NODE_ENV=test