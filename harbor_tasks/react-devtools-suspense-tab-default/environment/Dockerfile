FROM node:22-slim

# Install base dependencies
RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set git config
RUN git config --global user.email "dev@example.com" && \
    git config --global user.name "Developer"

WORKDIR /workspace

ARG BASE_COMMIT=8374c2abf13fa803233025192b8d7e87de70b087

# Clone React repo and create a sanitized snapshot
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/react

# Install minimal dependencies for testing (no build required for this task)
RUN npm install --legacy-peer-deps --ignore-scripts 2>/dev/null || \
    yarn install --ignore-scripts 2>/dev/null || \
    true

# Create minimal __tests__ directories for pass-to-pass validation
RUN mkdir -p packages/react-devtools-shared/src/__tests__

RUN mkdir -p /logs/verifier

ENV NODE_PATH=/workspace/react/packages
ENV CI=true
