FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (blobless for large monorepo)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout 5102fd079423e01019266560237667aad629588e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# No npm install needed — tests only exercise scripts/pr-status.js (built-in Node modules)
# and check agent config files (plain text)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
