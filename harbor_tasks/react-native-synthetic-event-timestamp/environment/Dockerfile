FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/react

# Clone React repo at base commit (pre-fix)
# Base commit: 074d96b9dd57ea748f2e869959a436695bbc88bf (parent of merge commit)
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent" && \
    git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin 074d96b9dd57ea748f2e869959a436695bbc88bf && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies
RUN yarn install --frozen-lockfile

# Configure git for any potential operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set up verifier logs directory
RUN mkdir -p /logs/verifier

# Set NODE_ENV for testing
ENV NODE_ENV=test

WORKDIR /workspace/react
