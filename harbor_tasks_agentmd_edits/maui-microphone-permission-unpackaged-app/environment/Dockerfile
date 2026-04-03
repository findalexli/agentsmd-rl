FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for large monorepo)
RUN git clone --depth=1 https://github.com/dotnet/maui.git /workspace/maui && \
    cd /workspace/maui && \
    git fetch --depth=1 origin 260770c977f376c9b0190c03ed1a41920725f079 && \
    git checkout 260770c977f376c9b0190c03ed1a41920725f079 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
