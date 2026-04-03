FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 bc \
    && rm -rf /var/lib/apt/lists/*

# Clone next.js at the base commit (before the fix)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin 04cc2f2ed2a2a65cf5ba78ea251be22a5f41e7c9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

# Configure git
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

ENV NODE_OPTIONS="--max-old-space-size=4096"