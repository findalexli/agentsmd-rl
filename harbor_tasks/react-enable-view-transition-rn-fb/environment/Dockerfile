FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Base commit (parent of merge commit for PR #36106)
ARG BASE_COMMIT=b4546cd0d4db2b913d8e7503bee86e1844073b2e
ARG REPO_URL=https://github.com/facebook/react

RUN mkdir -p /workspace && cd /workspace && \
    git clone --depth=1 "$REPO_URL" react && \
    cd react && \
    git fetch --depth=1 origin "$BASE_COMMIT" && \
    git checkout "$BASE_COMMIT" && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot at base commit"

WORKDIR /workspace/react

# Install minimal dependencies (yarn, no heavy packages needed)
RUN corepack enable && corepack prepare yarn@1.22.22 --activate

# Install node_modules during build so they're available for tests
RUN yarn install --frozen-lockfile --network-timeout 100000

RUN mkdir -p /logs/verifier
