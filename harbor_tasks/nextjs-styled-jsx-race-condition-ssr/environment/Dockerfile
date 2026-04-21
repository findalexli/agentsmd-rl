FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone next.js at the base commit (before PR #92459)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin 98330e3faeff95a51d2c185fc98f1f40bd86726f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

# Install tsx globally for running TypeScript directly
RUN npm install -g tsx

# Configure git
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

ENV NODE_OPTIONS="--max-old-space-size=4096"
