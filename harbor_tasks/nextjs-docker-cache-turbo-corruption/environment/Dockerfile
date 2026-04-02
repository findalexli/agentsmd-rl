FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone Next.js at the base commit (before the fix)
RUN git init /workspace/next.js \
    && cd /workspace/next.js \
    && git remote add origin https://github.com/vercel/next.js.git \
    && git fetch --depth=1 origin 7bce97d6485599cab2964ef58fde8a55d19904d3 \
    && git checkout FETCH_HEAD

# Configure git
RUN cd /workspace/next.js && \
    git config user.name "Agent" && \
    git config user.email "agent@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js