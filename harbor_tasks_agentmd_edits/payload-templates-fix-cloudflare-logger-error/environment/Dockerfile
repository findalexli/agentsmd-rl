FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (filter=blob:none for large monorepo)
RUN git clone --filter=blob:none https://github.com/payloadcms/payload.git /workspace/payload && \
    cd /workspace/payload && \
    git checkout 23d52a0d7d5780954bf5b027e537cabb008b8a0a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
