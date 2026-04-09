FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install bun for this repo
RUN curl -fsSL https://bun.sh/install | bash && \
    ln -s ~/.bun/bin/bun /usr/local/bin/bun

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout be9b4d1bcde39341c7813b66c5c19150a01bb8c2 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Install minimal deps for test runner (NOT full project deps)
RUN pip3 install --no-cache-dir pytest --break-system-packages 2>/dev/null || pip3 install --no-cache-dir pytest

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
