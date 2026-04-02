FROM node:22-slim

# Install system dependencies including git, python3 for scoring scripts
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/react

# Clone React repo at base commit (pre-fix) and create sanitized snapshot
ARG BASE_COMMIT=c6bb26bf833c5d91760daf28fa2750b81067ac30
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Install minimal dependencies for testing (react-devtools-shared tests)
# Only install what test.sh needs, skip heavy deps like React native tooling
RUN npm install --legacy-peer-deps || yarn install --frozen-lockfile || true

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
