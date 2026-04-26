FROM rust:1.86-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin a617c54b0708a8c1eb850cc3b2a5caee21137a28 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/ruff

# Install the required Rust toolchain (repo specifies 1.94 in rust-toolchain.toml)
RUN rustup toolchain install 1.94 && rustup default 1.94

# Pre-fetch cargo deps for faster agent builds
RUN cargo fetch

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
