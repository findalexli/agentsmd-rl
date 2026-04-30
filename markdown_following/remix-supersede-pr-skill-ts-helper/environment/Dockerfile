FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/remix && \
    cd /workspace/remix && \
    git remote add origin https://github.com/remix-run/remix.git && \
    git fetch --depth=1 origin 64b3a160dc25bbb082b96673e12bb55935f3528d && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
