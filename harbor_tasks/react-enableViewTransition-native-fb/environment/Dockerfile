FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates gnupg2 && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js (LTS) and yarn
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g yarn && \
    rm -rf /var/lib/apt/lists/*

# Clone react repo at base commit (shallow clone for large monorepo)
RUN git clone --depth=100 https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout b4546cd0d4db2b913d8e7503bee86e1844073b2e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
