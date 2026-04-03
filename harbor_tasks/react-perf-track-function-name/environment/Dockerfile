FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone React repo at base commit (pre-fix)
ENV REPO_DIR=/workspace/react
RUN mkdir -p $REPO_DIR
WORKDIR $REPO_DIR

ENV BASE_COMMIT=230772f99dac80be6dda9c59441fb4928612f18e
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin $BASE_COMMIT && \
    git checkout $BASE_COMMIT && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install yarn via corepack and dependencies
RUN corepack enable && corepack prepare yarn@1.22.22 --activate
RUN yarn install --frozen-lockfile --network-timeout=600000 || yarn install || true

# Configure git user for solve.sh
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR $REPO_DIR
