FROM oven/bun:1.2-slim

# Install python3 for the test runner
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip git curl ca-certificates build-essential \
        cmake ninja-build pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Install zig build dependencies needed for Bun
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        clang lld llvm && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (this is a large repo, use shallow clone)
RUN git clone --depth=100 --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 47af15f3f469b6325a01935b4373d36c98061cbd && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Install dependencies for testing
RUN bun install --frozen-lockfile 2>/dev/null || bun install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

# The test runner will execute from /workspace/bun
