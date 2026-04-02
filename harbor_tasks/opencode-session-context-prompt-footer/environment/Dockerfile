FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 tmux \
    && rm -rf /var/lib/apt/lists/*

# Install bun
RUN npm install -g bun@latest

# Clone repo at base commit (before fix)
RUN git clone https://github.com/anomalyco/opencode.git /workspace/opencode
RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
RUN git checkout 15a8c22a263b072a23e2fc0b2e840b2e12c220aa

# Install dependencies (needed for typecheck)
RUN bun install --frozen-lockfile || bun install

# Configure git for agent commits
RUN git config user.name "agent" && git config user.email "agent@test.com"

ENV PYTHONPATH=/
WORKDIR /workspace/opencode