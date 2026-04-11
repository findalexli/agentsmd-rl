FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for large monorepo)
RUN git clone --filter=blob:none https://github.com/cypress-io/cypress.git /workspace/cypress && \
    cd /workspace/cypress && \
    git checkout eb60ddcec6d92dad8ba1a1d776b249171384aa5e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/cypress

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
