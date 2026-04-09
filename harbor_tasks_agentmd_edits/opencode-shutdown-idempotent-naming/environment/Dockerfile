FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install system dependencies + python3 for test runner
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential unzip python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun

# Clone repo at base commit
ARG BASE_COMMIT=2a0be8316be7ae6ec78f5d221851fc1cc0cdddb2
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout $BASE_COMMIT && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Pre-install dependencies for faster test runs
RUN bun install || true

# Verifier output directory
RUN mkdir -p /logs/verifier
