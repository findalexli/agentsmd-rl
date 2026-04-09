FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use filter for speed)
RUN git clone --filter=blob:none https://github.com/storybookjs/storybook.git /workspace/storybook && \
    cd /workspace/storybook && \
    git checkout ce8c743b04264c5e8010df1181c828171a04c33a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/storybook

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
