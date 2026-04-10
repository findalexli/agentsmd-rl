FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Clone bun at base commit (before the fix)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 7960fe985dfa3418b507777a5a61289defbdb9dc && \
    git checkout FETCH_HEAD

# Install bun for running CI checks
RUN npm install -g bun

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun
