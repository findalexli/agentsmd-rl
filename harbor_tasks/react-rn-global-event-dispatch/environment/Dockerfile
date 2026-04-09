FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout a48e9e3f10fed06c813399ccae8a28db7dd76683 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
