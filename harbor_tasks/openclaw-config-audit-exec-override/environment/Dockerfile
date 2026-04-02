FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone repo at base commit (before fix)
RUN git clone https://github.com/openclaw/openclaw.git /workspace/openclaw && \
    cd /workspace/openclaw && \
    git checkout 1ca4261d7e055d0be141ed79ebb1365d0fbc7364 && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install dependencies
RUN pnpm install --frozen-lockfile || pnpm install

# Copy test harness

ENV PYTHONPATH=/tests
WORKDIR /workspace/openclaw