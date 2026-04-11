FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone React repo at base commit (parent of merge commit)
# Base commit: a74302c02d220e3663fcad5836cb90607fc2d006
RUN git clone --depth=1 --single-branch \
    https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin a74302c02d220e3663fcad5836cb90607fc2d006 && \
    git checkout a74302c02d220e3663fcad5836cb90607fc2d006

WORKDIR /workspace/react

# Configure git for any potential git operations (must be before git commit)
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Sanitize snapshot (remove git history, keep snapshot)
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies (yarn via corepack, just what we need to run tests)
RUN corepack enable && corepack prepare yarn@1.22.22 --activate

# Install dependencies (but skip heavy native build tools not needed for JS flag checking)
RUN yarn install --frozen-lockfile --network-timeout=600000 || yarn install

# Set up logging directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
