FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone React at base commit (pre-fix)
ARG BASE_COMMIT=2a879cdc95228b1b3b4cdc81cfc04599716b5562
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth 1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Clean git history to prevent accidental git-based solutions
RUN cd react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Install minimal dependencies needed to run the test
WORKDIR /workspace/react
RUN yarn install --frozen-lockfile --silent 2>/dev/null || yarn install --silent

# Create scoring directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
