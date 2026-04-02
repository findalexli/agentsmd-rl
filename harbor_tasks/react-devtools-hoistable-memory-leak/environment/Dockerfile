FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Base commit (parent of merge)
ENV BASE_COMMIT=49c3b270f9991fbecbe2b9c29c27e19a54fb4466
ENV REPO_DIR=/workspace/react

WORKDIR /workspace

# Clone and set up sanitized snapshot
RUN git clone --depth=1 https://github.com/facebook/react.git $REPO_DIR \
    && cd $REPO_DIR \
    && git fetch --depth=1 origin $BASE_COMMIT \
    && git checkout $BASE_COMMIT \
    && rm -rf .git \
    && git init \
    && git add -A \
    && git commit -m "snapshot"

WORKDIR $REPO_DIR

# Install minimal dependencies for testing
RUN yarn install --frozen-lockfile

# Set up git for potential patch operations
RUN git config --global user.email "agent@example.com" \
    && git config --global user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR $REPO_DIR
