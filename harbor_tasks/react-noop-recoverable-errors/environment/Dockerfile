FROM node:22-slim

# Install git and base dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone React at the pre-fix base commit (sanitized snapshot)
# Base commit: 23b2d8514f13f109b980b0a1f4f3aab906ad51d0
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin 23b2d8514f13f109b980b0a1f4f3aab906ad51d0 && \
    git checkout 23b2d8514f13f109b980b0a1f4f3aab906ad51d0 && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install yarn via corepack and dependencies
RUN corepack enable && corepack prepare yarn@1.22.22 --activate
WORKDIR /workspace/react
RUN yarn install --frozen-lockfile --network-timeout=600000 || yarn install

# Configure git for any future operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create test directories
RUN mkdir -p /logs/verifier /tests

WORKDIR /workspace/react
