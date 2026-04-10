FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (parent of merge commit for PR #9775)
RUN git clone --filter=blob:none https://github.com/biomejs/biome.git /workspace/biome && \
    cd /workspace/biome && \
    git checkout b22f31afd5e0d40cf5a2b10dad85accf7d34a2b8 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# Pre-fetch and pre-compile deps for the markdown parser crate
RUN cargo fetch


# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
