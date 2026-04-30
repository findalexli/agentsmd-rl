FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (BEFORE the fix)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 698eb8104be9a42c9a2b5e5b03a8843f81911055 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun