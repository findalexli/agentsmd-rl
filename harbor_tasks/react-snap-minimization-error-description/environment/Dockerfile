FROM node:22-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone at base commit and sanitize
ARG BASE_COMMIT=f84ce5a45c47b1081a09c17eea58c16ef145c113
WORKDIR /tmp
RUN git clone --depth 1 https://github.com/facebook/react.git repo && \
    cd repo && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Move to final location
WORKDIR /workspace/react
RUN mv /tmp/repo/* /workspace/react/ 2>/dev/null || true
RUN mv /tmp/repo/.??* /workspace/react/ 2>/dev/null || true

# Install dependencies for snap package (simplified)
WORKDIR /workspace/react/compiler
RUN yarn install --frozen-lockfile --network-timeout 600000 2>/dev/null || \
    (npm install --legacy-peer-deps && npm install --legacy-peer-deps)

# Set up workspace
ENV NODE_ENV=development
WORKDIR /workspace/react

# Create logs directory
RUN mkdir -p /logs/verifier
