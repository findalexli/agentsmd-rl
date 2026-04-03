FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --depth=1 https://github.com/payloadcms/payload.git /workspace/payload && \
    cd /workspace/payload && \
    git fetch --depth=1 origin a188556e99d94c96266671b2129e5c8cb05e46a5 && \
    git checkout a188556e99d94c96266671b2129e5c8cb05e46a5 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
