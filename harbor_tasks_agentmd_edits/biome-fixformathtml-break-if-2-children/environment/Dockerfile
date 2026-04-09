FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip pkg-config \
        libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (pre-fix)
RUN git clone --filter=blob:none https://github.com/biomejs/biome.git /workspace/biome && \
    cd /workspace/biome && \
    git checkout cb112ce872c8428414d78bc90c6ed26a102ac0e0 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# Pre-fetch Rust dependencies for faster agent builds
RUN cargo fetch 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
