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
    git checkout 69924568b93f2f37609fa2a617baf83d6ff11838 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install minimal deps needed by test_outputs.py
RUN pip3 install --no-cache-dir pytest --break-system-packages

# Install npm dependencies during build (needed for compilation)
RUN cd /workspace/playwright && npm ci

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
