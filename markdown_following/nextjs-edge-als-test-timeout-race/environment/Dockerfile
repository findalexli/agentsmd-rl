FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin 9f181bd11af5f532c529a6f168fe40505f0a4d75 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

# Configure git user for agent commits
RUN git config user.email "agent@test.com" && \
    git config user.name "Agent"

# No heavy deps needed — we only check test structure and fixture files