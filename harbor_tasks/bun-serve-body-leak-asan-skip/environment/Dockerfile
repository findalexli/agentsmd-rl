FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 66f7c41412e8a41c9686b0f4524b778a5f69b40e && \
    git checkout FETCH_HEAD

WORKDIR /workspace/bun