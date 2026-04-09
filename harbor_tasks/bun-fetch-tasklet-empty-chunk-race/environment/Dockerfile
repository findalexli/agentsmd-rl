FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install dependencies for building Bun
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential cmake ninja-build \
        python3 python3-pip python3-venv pkg-config \
        libssl-dev zlib1g-dev libzstd-dev \
        llvm-18 clang-18 lld-18 unzip && \
    rm -rf /var/lib/apt/lists/*

# Symlink LLVM tools
RUN ln -sf /usr/bin/llvm-ar-18 /usr/bin/llvm-ar && \
    ln -sf /usr/bin/llvm-objcopy-18 /usr/bin/llvm-objcopy && \
    ln -sf /usr/bin/llvm-objdump-18 /usr/bin/llvm-objdump && \
    ln -sf /usr/bin/clang-18 /usr/bin/clang && \
    ln -sf /usr/bin/clang++-18 /usr/bin/clang++

# Install Zig (Bun requires specific Zig version)
RUN curl -L https://ziglang.org/download/0.13.0/zig-linux-x86_64-0.13.0.tar.xz | tar -xJ -C /opt && \
    ln -s /opt/zig-linux-x86_64-0.13.0/zig /usr/local/bin/zig

# Install Bun (for build scripts)
RUN curl -fsSL https://bun.sh/install | bash && \
    ln -s ~/.bun/bin/bun /usr/local/bin/bun

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 770893d28ff94013abed5520482848609a6872f9 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Fetch submodules needed for build (shallow)
RUN git submodule update --init --depth=1 vendor/zig vendor/boringssl vendor/brotli vendor/cares \
    vendor/libarchive vendor/libdeflate vendor/libuv vendor/lolhtml vendor/lshpack \
    vendor/mimalloc vendor/picohttpparser vendor/zlib vendor/zstd 2>/dev/null || true

# Pre-fetch npm deps for build scripts
RUN cd /workspace/bun && bun install 2>/dev/null || true

# Install pytest for test runner
RUN pip3 install --break-system-packages pytest pytest-json-ctrf 2>/dev/null || \
    pip3 install pytest pytest-json-ctrf 2>/dev/null

# Verifier output directory
RUN mkdir -p /logs/verifier
