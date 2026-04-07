FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install TypeScript compiler globally (used by test_outputs.py for parse checks)
RUN npm install -g typescript

# Enable pnpm via corepack
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/effect-ts/effect.git /workspace/effect && \
    cd /workspace/effect && \
    git checkout 33712058e2655dd50f9b2b511ab8d38c2bd5268a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/effect

# Install dependencies (agent needs these for pnpm check/test/build)
RUN pnpm install --frozen-lockfile 2>&1 || pnpm install 2>&1

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
