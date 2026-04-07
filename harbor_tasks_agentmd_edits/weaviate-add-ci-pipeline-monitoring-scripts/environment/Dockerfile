FROM golang:1.24-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv jq && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/weaviate/weaviate.git /workspace/weaviate && \
    cd /workspace/weaviate && \
    git checkout 57d1e03321fd1648889b5c3fae5261cf5a7a0217 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/weaviate

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
