FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python3 for scoring
RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone React repo at base commit and create sanitized snapshot
WORKDIR /workspace
ARG BASE_COMMIT=705055d7ac3da03927758b22d8aea4b2e5913961
RUN git clone --no-checkout --depth 1 https://github.com/facebook/react.git react && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/react

# React DevTools doesn't need heavy build for our tests
# We'll just verify the JavaScript code structure

RUN mkdir -p /logs/verifier

# Copy test files
COPY tests/ /tests/
