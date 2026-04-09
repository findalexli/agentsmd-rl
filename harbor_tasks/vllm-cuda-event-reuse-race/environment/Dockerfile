FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo, use filter)
RUN git clone --filter=blob:none https://github.com/vllm-project/vllm.git /workspace/vllm && \
    cd /workspace/vllm && \
    git checkout b2b2c5239ec65fc6ba1109b0d06cb7462d99b70e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vllm

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
