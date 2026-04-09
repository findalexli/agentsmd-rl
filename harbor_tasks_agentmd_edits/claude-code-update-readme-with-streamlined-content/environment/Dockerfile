FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/anthropics/claude-code.git /workspace/claude-code && \
    cd /workspace/claude-code && \
    git checkout 0b881fcb4d7e0d223584aca58b27055084fffd0c && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/claude-code

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
