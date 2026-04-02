FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Clone repo at base commit (before the fix)
RUN git clone https://github.com/anomalyco/opencode.git /repo \
    && cd /repo \
    && git checkout 83ed1c4414859b53c91f1e2f6985c3498bac1e84

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install dependencies (only what's needed for type-checking and tests)
RUN bun install --frozen-lockfile || bun install

# Configure git
RUN git config user.name "test" && git config user.email "test@test.com"
