FROM rust:1.94-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/biomejs/biome.git /workspace/biome && \
    cd /workspace/biome && \
    git checkout 0bc2198735230c3bad14a831652543bd304fa0d6 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# Pre-fetch deps and build formatter test binary for fast incremental compilation
RUN cargo fetch
RUN cargo test -p biome_markdown_formatter --no-run 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
