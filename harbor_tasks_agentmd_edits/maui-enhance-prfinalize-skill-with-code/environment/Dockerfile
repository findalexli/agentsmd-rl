FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone maui repo at base commit (PR #33861 base)
RUN git clone --filter=blob:none https://github.com/dotnet/maui.git /workspace/maui && \
    cd /workspace/maui && \
    git checkout 64d90e3ca4e83cf44a7a75c5ffa95a3e7c3147b7 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
