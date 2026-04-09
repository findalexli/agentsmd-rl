FROM oven/bun:1.2-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux procps && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (opencode is a monorepo, use reasonable depth)
RUN git clone --depth=200 https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout 570038ac3c4ae02378e5de38793d3014587a33e1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Pre-install dependencies (this takes time, do it during build)
RUN bun install --frozen-lockfile 2>&1 || bun install 2>&1 || true

# Install minimal Python deps needed by test_outputs.py
RUN pip3 install --no-cache-dir --break-system-packages pytest 2>/dev/null || pip3 install --no-cache-dir pytest

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
