FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install dependencies for building Bun (zig, cmake, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip \
        cmake ninja-build clang lld zlib1g-dev libssl-dev \
        llvm liblld-18-dev libclang-18-dev \
        libbrotli-dev libarchive-dev libsqlite3-dev \
        wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Zig (required to build Bun)
RUN curl -L https://ziglang.org/download/0.13.0/zig-linux-x86_64-0.13.0.tar.xz | tar -xJ -C /usr/local && \
    ln -s /usr/local/zig-linux-x86_64-0.13.0/zig /usr/local/bin/zig

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 5b7fe81279a40f3fccebe6e7f52278c81b39dfb6 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Fetch submodules (needed for building)
RUN git submodule update --init --depth 1 --recursive || true

# Pre-fetch Zig dependencies
RUN zig fetch --help 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
