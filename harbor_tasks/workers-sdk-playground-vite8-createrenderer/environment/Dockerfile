FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone for speed)
RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git checkout 49d063396f4c87bc7323be84fbd961b010a09460 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workers-sdk

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
