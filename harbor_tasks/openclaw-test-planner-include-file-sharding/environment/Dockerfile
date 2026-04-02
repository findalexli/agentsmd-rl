FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone repo at base commit (before fix)
RUN git clone https://github.com/openclaw/openclaw.git /workspace/openclaw \
    && cd /workspace/openclaw \
    && git checkout c22edbb8eeb3668f60b0b23cd8e8e11b4340f6d6 \
    && git config user.email "agent@test" \
    && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install dependencies
RUN pnpm install --frozen-lockfile || pnpm install

ENV PYTHONPATH=/workspace/openclaw
WORKDIR /workspace/openclaw