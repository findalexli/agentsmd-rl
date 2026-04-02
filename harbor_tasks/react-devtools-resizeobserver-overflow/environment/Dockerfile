FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Set up git user for snapshot commit
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

WORKDIR /workspace

# Clone React repo at the base commit (parent of merge commit)
# base_commit = 3aaab92a265ebeb43b15e7c30c2f1dfb9fcd5961
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin 3aaab92a265ebeb43b15e7c30c2f1dfb9fcd5961 && \
    git checkout 3aaab92a265ebeb43b15e7c30c2f1dfb9fcd5961

WORKDIR /workspace/react

# Create sanitized snapshot (remove .git history)
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for testing
# We need the packages/react-devtools-shared to be available
RUN npm install --legacy-peer-deps 2>/dev/null || yarn install --frozen-lockfile 2>/dev/null || true

# Set up test directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
