FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 0b0ca631198af88cda1ecceef5a51d20e1b3b3e2 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# No project deps needed — tests only read file content and check structure
# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
