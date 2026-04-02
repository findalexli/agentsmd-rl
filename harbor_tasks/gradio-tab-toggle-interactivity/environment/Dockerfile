FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Shallow-clone gradio at the base commit (avoids full-history download)
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth 1 origin 75f8dceb679b505c8887f0a3c3b9fee98a931db9 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# TypeScript compiler for test parse checks
RUN npm install --prefix /tmp/ts typescript 2>/dev/null

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio