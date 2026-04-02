FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone React at the pre-fix base commit
WORKDIR /workspace
ARG BASE_COMMIT=e66ef6480ecd19c6885f2c06dec34fec1fdc0a98
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize snapshot - remove .git and reinit to get clean state
RUN cd /workspace/react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Install dependencies (minimal for testing)
RUN cd /workspace/react && yarn install --frozen-lockfile

# Set up workspace
WORKDIR /workspace/react
ENV NODE_ENV=development

# Create log directory
RUN mkdir -p /logs/verifier
