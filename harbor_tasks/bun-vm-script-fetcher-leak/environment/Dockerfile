FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 594f421fdc9a6aaf04b394e2775abc2f4baba05c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo