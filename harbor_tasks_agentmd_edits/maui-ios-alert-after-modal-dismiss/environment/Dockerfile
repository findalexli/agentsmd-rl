FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit — large monorepo, use treeless clone
RUN git clone --filter=tree:0 https://github.com/dotnet/maui.git /workspace/maui && \
    cd /workspace/maui && \
    git checkout 39325cec7d8a6de66e4608471b7843c7dfe3b4e1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
