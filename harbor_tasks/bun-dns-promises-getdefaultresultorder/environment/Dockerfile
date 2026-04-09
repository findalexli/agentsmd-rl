FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV BUN_INSTALL=/root/.bun
ENV PATH="${BUN_INSTALL}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Install dependencies: curl, git, build tools, python, and add LLVM repo for clang-21
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl ca-certificates git build-essential python3 python3-pip \
        cmake ninja-build wget gnupg unzip && \
    wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor > /usr/share/keyrings/llvm-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/llvm-archive-keyring.gpg] http://apt.llvm.org/noble/ llvm-toolchain-noble-21 main" > /etc/apt/sources.list.d/llvm.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends clang-21 lld-21 llvm-21 && \
    rm -rf /var/lib/apt/lists/*

# Create symlinks so bun can find clang
RUN ln -sf /usr/bin/clang-21 /usr/bin/clang && \
    ln -sf /usr/bin/clang++-21 /usr/bin/clang++ && \
    ln -sf /usr/bin/lld-21 /usr/bin/lld

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
