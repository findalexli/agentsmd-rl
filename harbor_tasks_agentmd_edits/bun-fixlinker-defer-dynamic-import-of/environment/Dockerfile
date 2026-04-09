FROM oven/bun:1.2.4
# Bun is a JavaScript runtime written in Zig
# We also need Zig for syntax checking the modified Zig source files

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Zig 0.14.0 (matching Bun's Zig version)
RUN curl -L https://ziglang.org/download/0.14.0/zig-linux-x86_64-0.14.0.tar.xz | tar -xJf - -C /opt && \
    ln -s /opt/zig-linux-x86_64-0.14.0/zig /usr/local/bin/zig

# Clone repo at base commit (use --depth=N for large monorepos)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 9a72bbfae2d086779739de54043a8e8bbd7ee9ed && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
