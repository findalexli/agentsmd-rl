FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/biomejs/biome.git /workspace/biome && \
    cd /workspace/biome && \
    git checkout 467fd87daec3d8c1fe64850a82480364480b313e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# Note: Pre-compilation skipped to avoid disk space issues during image export.
# Tests will be compiled on first run inside the container.

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
