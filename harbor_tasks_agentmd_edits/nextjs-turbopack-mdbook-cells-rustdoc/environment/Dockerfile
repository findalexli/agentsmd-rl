FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone next.js at the base commit with shallow history to save space
# Then remove unnecessary directories to save space
RUN git clone --depth=100 --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout 196ed2b83919892d45eaf7aed80852d0c9cc38c7 && \
    git config user.email "agent@test" && \
    git config user.name "Agent" && \
    rm -rf test examples docs scripts && \
    find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true

WORKDIR /workspace/next.js

# Pre-fetch Rust deps for faster agent builds (only turbo-tasks)
RUN cd turbopack/crates/turbo-tasks && cargo fetch 2>/dev/null || true

# Install minimal deps needed by test_outputs.py
RUN pip3 install --break-system-packages pytest pytest-json-ctrf 2>/dev/null || \
    python3 -m pip install pytest pytest-json-ctrf 2>/dev/null

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
