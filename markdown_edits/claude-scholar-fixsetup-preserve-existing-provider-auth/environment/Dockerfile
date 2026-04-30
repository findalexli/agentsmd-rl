FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/Galaxy-Dawn/claude-scholar.git /workspace/claude-scholar && \
    cd /workspace/claude-scholar && \
    git checkout d6fa24e0597692c21e16f976ec159a1482adcc2d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/claude-scholar

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
