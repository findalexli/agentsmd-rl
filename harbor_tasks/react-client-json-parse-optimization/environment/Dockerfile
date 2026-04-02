FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Shallow clone at base commit (parent of merge commit f247ebaf)
RUN git clone --depth 1 https://github.com/facebook/react.git react \
    && cd react \
    && git fetch --depth=1 origin 3a2bee26d23a21cfb04313372a0c0ca46101b785 \
    && git checkout 3a2bee26d23a21cfb04313372a0c0ca46101b785 \
    && rm -rf .git \
    && git init \
    && git add -A \
    && git commit -m "snapshot"

WORKDIR /workspace/react

# Install minimal dependencies for testing (React client package dependencies)
RUN yarn install --frozen-lockfile --network-timeout 600000

# Set up environment
ENV NODE_ENV=development
ENV CI=true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Configure git for any test that needs it
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"
