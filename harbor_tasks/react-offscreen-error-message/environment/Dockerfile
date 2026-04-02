FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create workspace and logs directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier /tests

# Clone React at the base commit (pre-fix)
# Using shallow clone for smaller image
ARG BASE_COMMIT=cd515d7e22636238adef912356f522168946313d
RUN git clone --depth 100 https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout $BASE_COMMIT && \
    rm -rf .git

# Re-initialize git for the snapshot pattern
WORKDIR /workspace/react
RUN git init && \
    git add -A && \
    git commit -m "snapshot at base commit"

# Install dependencies (yarn is the primary package manager for React)
RUN npm install -g yarn

# Install React dependencies
RUN yarn install --frozen-lockfile

# Ensure test logs directory exists
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
