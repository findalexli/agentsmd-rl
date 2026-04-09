FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux pkg-config libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (needed for cargo check/clippy tests)
ENV RUSTUP_HOME=/usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo
ENV PATH=/usr/local/cargo/bin:$PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --no-modify-path && \
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME

# Clone repo at base commit (shallow fetch — Deno is a large monorepo)
RUN git init /workspace/deno && \
    cd /workspace/deno && \
    git remote add origin https://github.com/denoland/deno.git && \
    git fetch --depth=1 origin d198cda44b7fddb56d892a8ef2349d1630adfa37 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/deno

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
