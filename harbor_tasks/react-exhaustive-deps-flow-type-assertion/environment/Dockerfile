FROM node:22-slim

# Install basic dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone React at base commit (parent of merge commit)
# Base commit: 22a20e1f2f557b99115d82b639ff5a32b6453cb6
ARG COMMIT_SHA=22a20e1f2f557b99115d82b639ff5a32b6453cb6
RUN git clone --depth=1 https://github.com/facebook/react.git react-repo && \
    cd react-repo && \
    git fetch --depth=1 origin ${COMMIT_SHA} && \
    git checkout ${COMMIT_SHA}

# Move to react-repo and sanitize (remove .git history)
RUN mv react-repo react && \
    cd react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "test@example.com" && \
    git config user.name "Test" && \
    git commit -m "snapshot"

# Install only eslint-plugin-react-hooks dependencies
WORKDIR /workspace/react/packages/eslint-plugin-react-hooks
RUN yarn install --frozen-lockfile --silent 2>/dev/null || yarn install --silent

# Configure for testing
WORKDIR /workspace/react
RUN git config user.email "agent@example.com" && \
    git config user.name "Agent"

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
