FROM oven/bun:1.2-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install git, python3, nodejs, npm and other build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip python3-venv nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout d4694d058cc590b0f05261a04460034d2fa8541d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Install dependencies (needed for tsc checks)
RUN bun install || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
