FROM oven/bun:1-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin 2aae0d3493ac51aa2fd3929c6db0814ab795b04b && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Install dependencies for testing
RUN cd /workspace/opencode/packages/opencode && bun install || true

# Verifier output directory
RUN mkdir -p /logs/verifier
