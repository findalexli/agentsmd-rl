FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/openclaw && \
    cd /workspace/openclaw && \
    git remote add origin https://github.com/openclaw/openclaw.git && \
    git fetch --depth=1 origin 8db20c196598b12043886ddc1c3ec0fd7695b9b4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install deps — tests need vitest and the full project to run install.test.ts
RUN corepack enable && corepack prepare pnpm@latest --activate && \
    pnpm install --frozen-lockfile

# Tests, rubric, and instruction are volume-mounted at runtime