# React DevTools ContextMenu null ref fix
FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone React at pre-fix commit (base commit = parent of merge commit)
ARG BASE_COMMIT=93882bd40ee48dc6d072dfc0b6cc7801fac1be31
RUN git clone --depth=100 --no-single-branch https://github.com/facebook/react.git react

WORKDIR /workspace/react
RUN git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    git clean -fdx

# Remove git history for sanitized snapshot
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Set up minimal dependencies: just what's needed for testing ContextMenu
# React uses yarn, so install dependencies
RUN yarn install --frozen-lockfile || yarn install

# Configure git user for patches
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set up Python3 for any scoring scripts
ENV PYTHONUNBUFFERED=1

# Create verifier log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react/packages/react-devtools-shared/src/devtools/ContextMenu
