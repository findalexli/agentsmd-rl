FROM rust:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git python3 python3-pip ca-certificates pkg-config tmux && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /logs/verifier

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git /workspace/uv && \
    cd /workspace/uv && \
    git checkout 30e33420497d6d493d70895291e849f5dcf4f2b5 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/uv

# Install the required Rust toolchain (matches rust-toolchain.toml)
RUN rustup install 1.94.0 && rustup default 1.94.0

# Pre-fetch and pre-compile dependencies for faster test execution
RUN cargo fetch
RUN cargo test --package uv-platform-tags --package uv-distribution-filename --no-run 2>&1 || true
