FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit -- turbopack is large, use --depth=200
RUN git clone --depth=200 --filter=blob:none https://github.com/vercel/next.js.git /workspace/nextjs && \
    cd /workspace/nextjs && \
    git fetch --depth=200 origin b2f193b0964212c3ef0213efb74fe40dfd5be43b && \
    git checkout b2f193b0964212c3ef0213efb74fe40dfd5be43b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/nextjs

# Pre-fetch Rust deps for the turbo-persistence crate to speed up compilation
RUN cd turbopack/crates/turbo-persistence && cargo fetch 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
