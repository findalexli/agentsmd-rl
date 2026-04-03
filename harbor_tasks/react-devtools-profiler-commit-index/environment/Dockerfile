FROM node:22-slim

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential python3 \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /workspace

# Base commit parent of fb/react#35672 merge
ENV BASE_COMMIT=748ee74e22ab86994c12564a9fc73950d00ad72

# Clone React repo at base commit with sanitized snapshot
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/react

# Configure git user for any patches
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Verify repo structure exists
RUN ls packages/react-devtools-shared/src/devtools/views/Profiler/

# Create verifier/logs directory
RUN mkdir -p /logs/verifier
