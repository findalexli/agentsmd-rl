FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV BUN_INSTALL=/root/.bun
ENV PATH="${BUN_INSTALL}/bin:${PATH}"

# Install dependencies: curl, git, build tools, python, and unzip for bun install
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl ca-certificates git build-essential python3 python3-pip \
        cmake ninja-build clang llvm lld unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Bun (needed for the build system)
RUN curl -fsSL https://bun.sh/install | bash

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 0ff0065f9e5a34c26bd8d1bede19d4239bb95b55 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Pre-install dependencies to speed up builds
RUN bun install 2>&1 || true

# Fetch WebKit and other large deps in advance (takes time but speeds up agent)
RUN bun run build --download 2>&1 || true

# Verifier output directory
RUN mkdir -p /logs/verifier
