FROM node:22-slim

# Install dependencies
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

# Clone React repository at the base commit (parent of merge commit)
ARG BASE_COMMIT=0dbb43bc57d27a79ecf4c78508089a36bd08ef5d
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Clean git history for security and create a snapshot commit
RUN cd react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for testing the React Compiler
RUN cd react/compiler && \
    yarn install --frozen-lockfile

# Set up environment
ENV NODE_ENV=test
WORKDIR /workspace/react/compiler/packages/babel-plugin-react-compiler

# Create logs directory
RUN mkdir -p /logs/verifier

# Configure git user for any git operations during solve
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"
