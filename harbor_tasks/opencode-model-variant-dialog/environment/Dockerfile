FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun (opencode uses bun)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Clone repo at base commit (before the fix)
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin 8ac2fbbd1262a9de1362beb6e29debc446ceea0e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

# Configure git user for patch application
RUN git config user.email "test@test.com" && git config user.name "Test"

# Install dependencies (only what's needed for type checking the TUI components)
RUN bun install --frozen-lockfile || bun install

ENV PYTHONPATH="/workspace/opencode"