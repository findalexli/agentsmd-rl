FROM debian:12-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    xz-utils \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Zig
RUN curl -L https://ziglang.org/download/0.14.0/zig-linux-x86_64-0.14.0.tar.xz | tar -xJ -C /usr/local \
    && ln -s /usr/local/zig-linux-x86_64-0.14.0/zig /usr/local/bin/zig

# Clone bun repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git bun \
    && cd bun \
    && git checkout 49221ca7440128b32222aefd0df53c359b3fd5fd

RUN mkdir -p /logs/verifier
WORKDIR /workspace/bun
