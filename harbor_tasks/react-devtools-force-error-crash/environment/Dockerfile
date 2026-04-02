FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone React at the base commit (before the fix)
ARG BASE_COMMIT=4610359651fa10247159e2050f8ec222cb7faa91
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/react

# Install dependencies (Node.js project)
RUN yarn install --frozen-lockfile 2>&1 || yarn install 2>&1

# Clean git history for space, re-init as fresh repo
RUN rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
