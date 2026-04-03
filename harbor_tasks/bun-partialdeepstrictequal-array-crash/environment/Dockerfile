FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone bun repo at the base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin e59a147d615a0b95d446c75ba836717cf0dbc513 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo