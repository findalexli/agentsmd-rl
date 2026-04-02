FROM node:22-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone React repo at base commit (pre-fix)
ARG BASE_COMMIT=74568e8627aa43469b74f2972f427a209639d0b6
RUN git clone --depth=50 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    git checkout -b base && \
    git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set working directory to the compiler playground
WORKDIR /workspace/react/compiler/apps/playground

# Install dependencies (minimal - just for playground)
RUN npm install --legacy-peer-deps 2>&1 || yarn install 2>&1 || true

# Install json5 explicitly
RUN npm install json5@^2.2.3 --legacy-peer-deps 2>&1 || yarn add json5@^2.2.3 2>&1 || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
ENV PATH="/workspace/react/compiler/apps/playground/node_modules/.bin:${PATH}"
