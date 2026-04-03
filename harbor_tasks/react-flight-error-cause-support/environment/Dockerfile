FROM node:22-slim

# Install system dependencies + Python for test scoring
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Base commit (parent of merge commit for PR #35810)
ARG BASE_COMMIT=38cd020c1fb8a1e88b7852160796f411926a6fac

# Clone React repo at specific commit with shallow history (no git history)
RUN git clone --no-checkout --depth=1 https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/react

# Configure git (for the snapshot)
RUN git config user.email "agent@example.com" && \
    git config user.name "Agent"

# Install yarn via corepack and dependencies
RUN corepack enable && corepack prepare yarn@1.22.22 --activate
RUN yarn install --frozen-lockfile --network-timeout=600000 || yarn install

# Build packages needed for Flight tests (ReactNoop builds)
RUN yarn build react/index,react-dom/index,react-server/react-flight --type=NODE_DEV || true

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV CI=true
ENV NODE_ENV=development
ENV WORKDIR=/workspace/react
