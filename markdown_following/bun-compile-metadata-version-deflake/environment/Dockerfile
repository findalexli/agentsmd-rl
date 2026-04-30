FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (BEFORE the fix)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin a04817ce2b7f1a1e8b7cbf8af8f2c027ab072f1d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun