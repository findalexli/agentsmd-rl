FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone repo at base commit (before fix)
RUN git init /workspace/openclaw && \
    cd /workspace/openclaw && \
    git remote add origin https://github.com/openclaw/openclaw.git && \
    git fetch --depth=1 origin aff6883f93abcbfd18ebb743871bc804b10f5728 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install dependencies
RUN pnpm install --frozen-lockfile || pnpm install

# Pre-install tsx and esbuild so tests don't need network
RUN npx --yes tsx --version && npx --yes esbuild --version

ENV PYTHONPATH=/tests
WORKDIR /workspace/openclaw