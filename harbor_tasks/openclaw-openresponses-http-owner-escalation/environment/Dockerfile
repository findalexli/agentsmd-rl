FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone repo at base commit (BEFORE the fix)
RUN git clone https://github.com/openclaw/openclaw.git /workspace/openclaw && \
    cd /workspace/openclaw && \
    git checkout 1a75906a6fe5191ea573758017834f200056500b && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install dependencies (needed for TypeScript compilation and test running)
RUN pnpm install --frozen-lockfile 2>/dev/null || pnpm install
