FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 1bebb2d1759a9df0c676eb0708451abf90973fcc && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install dependencies for the html-reporter package
RUN npm ci --prefix packages/html-reporter 2>/dev/null || true
RUN npm ci 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
