FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git checkout 7d318e1b7e5af62c0ed09d3e5a51af84294c372e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workers-sdk

RUN mkdir -p /logs/verifier
