FROM node:22-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt-get

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set working directory
WORKDIR /workspace/react

# Clone at specific commit and create clean snapshot
ARG BASE_COMMIT=57b79b0388b755096216b2b5308113e54eac3be8
RUN git clone --depth 1 https://github.com/facebook/react.git . && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot at base commit"

# Install dependencies (React monorepo uses yarn)
RUN yarn install --frozen-lockfile --network-timeout 100000

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set PYTHONPATH for any Python tests
ENV PYTHONPATH=/workspace/react:$PYTHONPATH
