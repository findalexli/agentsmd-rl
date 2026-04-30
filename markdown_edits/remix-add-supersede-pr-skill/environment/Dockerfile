FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 64b3a160dc25bbb082b96673e12bb55935f3528d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Install dependencies
RUN pnpm install

RUN mkdir -p /logs/verifier
