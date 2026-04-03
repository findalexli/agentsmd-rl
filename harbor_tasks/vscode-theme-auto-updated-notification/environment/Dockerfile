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

# Clone VS Code repo at base commit (pre-fix)
ARG BASE_COMMIT=9d3144bf84f54ab1e886fca20608dd3ddc296f64
RUN git clone --depth=1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Remove git history to create sanitized snapshot
WORKDIR /workspace/vscode
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Set up logs directory
RUN mkdir -p /logs/verifier

# IMPORTANT: VS Code needs full build - but test.sh will only compile-check the changed file
# We'll set up npm but not do full compilation (too heavy for test container)
WORKDIR /workspace/vscode
