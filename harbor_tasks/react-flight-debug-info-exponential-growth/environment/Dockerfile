FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
ENV BASE_COMMIT=e8c6362678c8bc86a02b8444d2c3f597b3dc4e22
WORKDIR /workspace/react

# Clone React repo at specific commit (shallow clone)
RUN git clone --depth 1 https://github.com/facebook/react.git . && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies
RUN yarn install --frozen-lockfile

# Prepare a sanitized snapshot (no .git history) to reduce image size
# but keep git working for potential patch operations
RUN git reset --hard ${BASE_COMMIT} && \
    rm -rf .git/hooks && \
    git config user.email "test@example.com" && \
    git config user.name "Test User"

# Create verifier directories
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
ENV CI=true
WORKDIR /workspace/react
