FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV CARGO_PROFILE_DEV_OPT_LEVEL=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git /workspace/ruff && \
    cd /workspace/ruff && \
    git checkout ee9084695ec4d70bc66083ac2b3cf598cc45101a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/ruff

# Pre-build ty type checker binary (cached in Docker image)
RUN cargo build --bin ty 2>&1

RUN mkdir -p /logs/verifier
