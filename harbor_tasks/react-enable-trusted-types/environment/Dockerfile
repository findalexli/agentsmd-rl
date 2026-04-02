FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/react

# Create a pseudo-user for git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone React at base commit and sanitize
RUN git clone --depth=1 https://github.com/facebook/react.git . && \
    git fetch --depth=1 origin e33071c6142ae5212483a63b87d5d962860e535a && \
    git checkout e33071c6142ae5212483a63b87d5d962860e535a && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies
RUN yarn install --frozen-lockfile 2>&1 || yarn install

# Create logs directory
RUN mkdir -p /logs/verifier

ENV NODE_ENV=test
WORKDIR /workspace/react
