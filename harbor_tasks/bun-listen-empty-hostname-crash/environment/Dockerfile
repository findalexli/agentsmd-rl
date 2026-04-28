FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun with pinned version for reproducibility
RUN curl -fsSL https://bun.sh/install | bash -s "bun-v1.3.13"
ENV PATH="/root/.bun/bin:${PATH}"

ARG BASE_COMMIT=73361607d70bd77041d0fc20e45a6dbe2373a677

# Shallow-fetch only the target commit (bun repo is very large)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth 1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun

# Configure git user for agent commits
RUN git config user.name "agent" && git config user.email "agent@test.local"
