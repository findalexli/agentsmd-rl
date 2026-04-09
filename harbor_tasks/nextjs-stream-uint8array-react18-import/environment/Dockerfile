FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout 9cb2048439b8b95b6e6460d17d94d9cb1823fbef && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
