FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone for speed)
RUN git clone --filter=blob:none https://github.com/TryGhost/Ghost.git /workspace/Ghost && \
    cd /workspace/Ghost && \
    git checkout 3ad6d52705c5e7b49831900424000b93fa41e90f && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/Ghost

# Install only semver (needed by create-migration.js) — skip full monorepo install
RUN cd ghost/core && npm install --no-save semver 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
