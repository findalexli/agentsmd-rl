FROM node:22-slim

# Install git, python3 for pytest runner, and bun dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Setup workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone the repo at base commit (pre-fix state)
ARG REPO_URL=https://github.com/anomalyco/opencode.git
ARG BASE_COMMIT=28bb16ca2a374439973d4f3f4b71d72f7fdae9cd

RUN git clone --filter=blob:none $REPO_URL opencode && \
    cd opencode && \
    git checkout $BASE_COMMIT

# Install dependencies (just for type checking, not running actual e2e tests)
WORKDIR /workspace/opencode
RUN bun install || true

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
