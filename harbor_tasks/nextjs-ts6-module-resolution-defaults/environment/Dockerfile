FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

# Clone at base commit (before fix)
RUN git init /workspace/repo && \
    cd /workspace/repo && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin 7dd1fcfc924be23cf2785054f5a2ad4f5affb692 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/repo

# Create dist/compiled symlink so `next/dist/compiled/*` resolves to src/compiled/*
RUN mkdir -p packages/next/dist && \
    ln -s /workspace/repo/packages/next/src/compiled /workspace/repo/packages/next/dist/compiled

# Create node_modules symlink so bare `next` resolves to packages/next
RUN mkdir -p node_modules && \
    ln -s /workspace/repo/packages/next node_modules/next

# Install tsx for running TypeScript directly, plus typescript for config tests
RUN npm install --no-save tsx typescript@5.9.2

# Git config for agent
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/repo