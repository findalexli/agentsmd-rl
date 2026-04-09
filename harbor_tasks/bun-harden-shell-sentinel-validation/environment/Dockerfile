FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Bun (needed for tests that run TypeScript)
RUN curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun

# Clone repo at base commit (bun repo, PR 27506)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout f06119ad0cd49bba93908329ef5e53a39c50fb70 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
