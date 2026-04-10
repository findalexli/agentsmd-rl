FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && pip3 install --break-system-packages pytest pytest-json-ctrf \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/react

# Configure git (must be before git commit)
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone repo at base commit (sanitized snapshot)
ARG BASE_COMMIT=ff191f24b5f49252672ac4d3c46ef1e79cf7290d
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies (only what's needed for tests)
RUN yarn install --frozen-lockfile

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
