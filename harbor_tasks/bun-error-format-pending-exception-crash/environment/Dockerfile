FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin f6528b58ed67c8fb8c80046114829d9ad79a292f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo