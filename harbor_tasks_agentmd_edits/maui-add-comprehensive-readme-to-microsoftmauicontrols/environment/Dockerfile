FROM mcr.microsoft.com/dotnet/sdk:8.0

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (use --filter=blob:none for large monorepos)
RUN git clone --filter=blob:none https://github.com/dotnet/maui.git /workspace/maui && \
    cd /workspace/maui && \
    git checkout d2e5dfa5d0b19e4c306e9f4cef62f72c845ef726 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
