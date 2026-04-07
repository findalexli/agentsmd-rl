FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Enable pnpm via corepack (reads packageManager from package.json)
RUN corepack enable

# Clone repo at base commit
RUN git clone --filter=blob:none --single-branch https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 89db125c56d3b0d637a283ac9122c6cb8f5542c3 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Install only data-table and data-schema deps (monorepo is large)
RUN pnpm install --filter @remix-run/data-table...

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
