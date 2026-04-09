FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 3cdf7ca18324b9a0aa0ec80d818c2f9602b0ef60 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install npm dependencies (required for npm run check-deps and other scripts)
RUN npm ci

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
