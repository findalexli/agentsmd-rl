FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin 9f94bdb49634bda90a2804585b8d739228dde876 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential commits
RUN git config user.email "agent@test" && git config user.name "Agent"

ENV PYTHONPATH=/repo