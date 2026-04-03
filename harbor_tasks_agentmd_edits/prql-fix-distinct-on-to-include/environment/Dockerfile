FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PRQL/prql.git /workspace/prql && \
    cd /workspace/prql && \
    git checkout 7b0d983ead8d91921252ad835a3c43b2288b7fe1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prql

# Pre-build prqlc to warm cargo cache — agent only needs incremental recompile
RUN cargo build -p prqlc 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
