FROM rust:1-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential pkg-config tmux \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/uv && \
    cd /workspace/uv && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 5108919f039509703656f394cb647bc01dd09766 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/uv

# Pre-fetch deps to speed up test-time compilation
RUN cargo fetch

# Pre-compile the target crate in test mode so only changed files recompile
RUN cargo test -p uv-distribution-types --no-run 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
