FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (use --depth=20 for recent history)
RUN git clone --depth=20 --filter=blob:none https://github.com/payloadcms/payload.git /workspace/payload && \
    cd /workspace/payload && \
    git fetch --depth=20 origin fdea8d8457fafe59be4b877a52a00990a735fd38 && \
    git checkout fdea8d8457fafe59be4b877a52a00990a735fd38 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
