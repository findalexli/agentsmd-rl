FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install dependencies: git, curl, python3, and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip \
        cmake ninja-build pkg-config libssl-dev zlib1g-dev \
        llvm clang lld && \
    rm -rf /var/lib/apt/lists/*

# Install Zig (Bun requires specific Zig version)
RUN curl -fsSL https://ziglang.org/download/0.13.0/zig-linux-x86_64-0.13.0.tar.xz | \
    tar -xJf - -C /opt && \
    ln -s /opt/zig-linux-x86_64-0.13.0/zig /usr/local/bin/zig

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 686eda3cb4773bb1ffe77cbdef6d0507d8fc2314 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Verifier output directory
RUN mkdir -p /logs/verifier
