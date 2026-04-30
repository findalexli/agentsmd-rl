FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow)
RUN git init /workspace/prql && \
    cd /workspace/prql && \
    git remote add origin https://github.com/PRQL/prql.git && \
    git fetch --depth=1 origin 76deaddd5dbbe8548672777ed5a4d6ac10d92171 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prql

# Pre-fetch and check deps so incremental builds are fast
RUN cargo fetch
RUN cargo check -p prqlc 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
