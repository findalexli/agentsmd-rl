FROM oven/bun:1.2-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux procps && \
    rm -rf /var/lib/apt/lists/*

# Copy local repo copy (commit already at 570038ac3c4ae02378e5de38793d3014587a33e1)
COPY repo /workspace/opencode
RUN cd /workspace/opencode && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Pre-install dependencies (this takes time, do it during build)
RUN bun install --frozen-lockfile 2>&1 || bun install 2>&1 || true

# Install minimal Python deps needed by test_outputs.py
RUN pip3 install --no-cache-dir --break-system-packages pytest pytest-json-ctrf 2>/dev/null || pip3 install --no-cache-dir pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
