FROM node:22-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone React repository at the base commit (pre-fix state)
# Base commit: e6f1c33acf81d9865863ab149d24726f43a56db0
RUN git clone --depth 100 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin e6f1c33acf81d9865863ab149d24726f43a56db0 && \
    git checkout e6f1c33acf81d9865863ab149d24726f43a56db0

WORKDIR /workspace/react

# Install dependencies
RUN yarn install --frozen-lockfile

# Sanitize the snapshot (remove .git history for reproducibility)
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Configure git user
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set up test runner environment
ENV NODE_ENV=test
ENV CI=true

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
