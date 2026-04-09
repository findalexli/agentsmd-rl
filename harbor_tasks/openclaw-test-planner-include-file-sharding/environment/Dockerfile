FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone repo at base commit (before fix)
RUN git init /workspace/openclaw && \
    cd /workspace/openclaw && \
    git remote add origin https://github.com/openclaw/openclaw.git && \
    git fetch --depth=1 origin c22edbb8eeb3668f60b0b23cd8e8e11b4340f6d6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install dependencies with memory limit to prevent OOM
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN pnpm install --frozen-lockfile || pnpm install

ENV PYTHONPATH=/workspace/openclaw
WORKDIR /workspace/openclaw
