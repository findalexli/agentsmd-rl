FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux jq python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use depth limit)
RUN git init /workspace/payload && \
    cd /workspace/payload && \
    git remote add origin https://github.com/payloadcms/payload.git && \
    git fetch --depth=1 origin 80d7781b4f2fc2e874323532a0a8a8da65c8fc22 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
