FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git /workspace/router && \
    cd /workspace/router && \
    git checkout aa68f71febbfc2f751fd3f2252bc42c27c939835 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/router

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
