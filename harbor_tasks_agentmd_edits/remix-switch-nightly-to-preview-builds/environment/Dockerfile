FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Remix is a large monorepo — use depth limit for faster clone
RUN git clone --depth=1000 https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 721dac4c6704d5b3e8428887af21accdcb3b23ea && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
