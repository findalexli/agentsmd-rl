FROM node:22-slim

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate
RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/Effect-TS/effect.git /workspace/effect && \
    cd /workspace/effect && \
    git checkout 4d97a61a15b9dd6a0eece65b8f0c035e16d42ada

WORKDIR /workspace/effect
RUN pnpm install

RUN mkdir -p /logs/verifier
