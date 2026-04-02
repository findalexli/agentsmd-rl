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
WORKDIR /workspace

# Clone React repo at base commit (pre-fix)
ARG BASE_COMMIT=4c9d62d2b47be424ad9050725d8bdd8df12fe2a3
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/react

# Install dependencies (DevTools tests need the monorepo setup)
RUN yarn install --frozen-lockfile

# Verify the file exists that we'll be testing
RUN test -f packages/react-devtools-shared/src/backend/fiber/renderer.js || \
    (echo "renderer.js not found at expected path" && exit 1)

# Configure git
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

# Create test directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
