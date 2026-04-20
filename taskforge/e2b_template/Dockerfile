FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git jq ripgrep python3 python3-pip python3-venv \
    ca-certificates gnupg lsb-release sudo \
    && rm -rf /var/lib/apt/lists/*

# Docker (runs natively in Firecracker microVM)
RUN curl -fsSL https://get.docker.com | sh

# Node.js 22 + Claude Code CLI + Gemini CLI
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @anthropic-ai/claude-code@latest @google/gemini-cli

# GitHub CLI (for scaffold PR fetching)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    gpg --dearmor -o /usr/share/keyrings/githubcli.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/githubcli.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && apt-get install -y gh

# Python test deps + litellm for Gemini proxy
RUN pip3 install --break-system-packages pytest pyyaml "litellm[proxy]"

# Non-root user for claude -p (refuses --dangerously-skip-permissions as root)
RUN useradd -m -s /bin/bash worker && \
    mkdir -p /workspace/task /logs/verifier && \
    chown -R worker:worker /workspace /logs/verifier

WORKDIR /workspace
