# Dockerfile for react-devtools-activity-reveal task
FROM node:22-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone React repo at the buggy commit (parent of merge commit)
# Base commit: 24f215ce8b0e17a230fbb7317919a6ae0c324f35
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth 1 origin 24f215ce8b0e17a230fbb7317919a6ae0c324f35 && \
    git checkout 24f215ce8b0e17a230fbb7317919a6ae0c324f35

WORKDIR /workspace/react

# Configure git user
RUN git config user.email "agent@example.com" && \
    git config user.name "Agent"

# Sanitize: remove .git history but keep code
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install yarn
RUN npm install -g yarn

# Install minimal dependencies (just what we need for testing)
# Note: The test framework is Jest-based within the repo
RUN yarn install --frozen-lockfile

# Create test/output directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
