FROM node:22-slim

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
RUN mkdir -p /logs/verifier

# Clone React repo at the pre-fix base commit
# Using shallow clone for smaller image
ARG BASE_COMMIT=6066c782fe06b65e98a410741d994f620321fe11
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize: remove .git history but keep files
RUN cd react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot at base commit"

# Install minimal dependencies (only what's needed for testing)
# React DevTools uses yarn, install dependencies for the specific package
WORKDIR /workspace/react
RUN yarn install --frozen-lockfile --production=false

# Set working directory to the devtools package for convenience
WORKDIR /workspace/react/packages/react-devtools-shared
