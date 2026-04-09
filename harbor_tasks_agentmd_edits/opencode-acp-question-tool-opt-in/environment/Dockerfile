FROM oven/bun:1-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout 86e545a23ecdb2c1840ab01e82eca292117c6bbc && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Install bun dependencies for the package
RUN cd /workspace/opencode/packages/opencode && bun install || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
