FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone repo at base commit (before the fix)
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin 47d2ab120a4fbc92e72aca4d5b40d722d0e4d2be && \
    git checkout FETCH_HEAD

WORKDIR /workspace/opencode

# Configure git
RUN git config user.email "agent@test.com" && git config user.name "Agent"

# Install deps for typecheck only (no full build needed)
RUN bun install --frozen-lockfile || bun install
