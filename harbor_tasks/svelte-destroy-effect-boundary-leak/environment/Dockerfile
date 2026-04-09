FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip python3-venv tmux && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

RUN git clone --filter=blob:none https://github.com/sveltejs/svelte.git /workspace/svelte && \
    cd /workspace/svelte && \
    git checkout 6b33dd2a1e8aa48dc88c9ce6e19c4a49a2eac51a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/svelte

# Install dependencies
RUN pnpm install

RUN mkdir -p /logs/verifier
