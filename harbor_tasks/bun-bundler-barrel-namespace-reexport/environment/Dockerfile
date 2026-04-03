FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun for running JS tests
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Clone bun repo at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun \
    && cd /workspace/bun \
    && git checkout 1628bfeceb07085263b5da5adb1ec3b094e4b188

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun

# Configure git user for agent commits
RUN git config user.name "agent" && git config user.email "agent@test.local"

# Copy test and evaluation files (mounted at runtime, not baked in)