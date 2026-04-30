FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip pkg-config tmux && \
    rm -rf /var/lib/apt/lists/*

# Repo requires nightly-2026-02-05 (see rust-toolchain.toml)
RUN rustup toolchain install nightly-2026-02-05 --profile minimal && \
    rustup default nightly-2026-02-05

# next.js is a large monorepo — shallow clone at base commit
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin fc13ca90ab14987da0b9bc556fc4c7e9e1b531af && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Pre-fetch cargo deps for faster agent builds
RUN cargo fetch --manifest-path Cargo.toml 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
