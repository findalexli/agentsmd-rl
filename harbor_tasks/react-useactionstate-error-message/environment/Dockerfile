FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git user
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone React repository at base commit
WORKDIR /workspace
RUN git clone --no-checkout https://github.com/facebook/react.git react
WORKDIR /workspace/react

# Base commit: parent of merge commit 93882bd40ee48dc6d072dfc0b6cc7801fac1be31
ARG BASE_COMMIT=3bc2d414287e62a7b74731c6c7b837270353a339
RUN git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize snapshot - remove .git history and re-init
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for testing (yarn needed for React)
RUN npm install -g yarn

# Install dependencies (React uses yarn)
RUN yarn install --frozen-lockfile 2>&1 || yarn install

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
