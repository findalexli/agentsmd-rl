FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential \
        cmake ninja-build clang llvm \
        ruby perl pkg-config libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Clone Bun repo at base commit (large repo, use blob filter)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout fe4a66e086bebd2c3c5a238effa801426d736278 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
