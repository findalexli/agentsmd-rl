FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/openclaw && \
    cd /workspace/openclaw && \
    git remote add origin https://github.com/openclaw/openclaw.git && \
    git fetch --depth=1 origin 7e086697152920c48651276ed8ae9c27354c092d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install pnpm and deps for running vitest
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install --frozen-lockfile || pnpm install

# Tests, rubric, and instruction are volume-mounted at runtime
RUN mkdir -p /tests