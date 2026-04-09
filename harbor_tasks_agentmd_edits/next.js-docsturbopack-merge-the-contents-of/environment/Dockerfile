FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout 545eba1ff6a6e74042c6e9c7412e3315a6f36d19~1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Pre-fetch rust deps for faster builds (optional but helpful)
RUN cd turbopack/crates/turbo-tasks && cargo fetch 2>/dev/null || true

# Verifier output directory
RUN mkdir -p /logs/verifier
