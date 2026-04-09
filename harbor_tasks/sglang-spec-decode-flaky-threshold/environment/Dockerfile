FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout 1ad6839659085732a6fe308f97141841d67f6323 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
