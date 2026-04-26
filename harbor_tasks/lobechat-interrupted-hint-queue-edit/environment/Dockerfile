FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git remote add origin https://github.com/lobehub/lobe-chat.git && \
    git fetch --depth=1 origin 9c08fa5cdf2116e041b63255be3e498f1ae8d1e3 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lobe-chat

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
