FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git /workspace/ruff && \
    cd /workspace/ruff && \
    git checkout 5fd492a95721a158c54d60349b54e5fe4b7cd874 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/ruff

# Pre-fetch deps and pre-build the affected crate
RUN cargo fetch 2>&1 || true
RUN cargo check -p ty_python_semantic 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
