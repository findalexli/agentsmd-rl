FROM python:3.12-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git
WORKDIR /workspace/langchain

# Checkout base commit (parent of merge commit)
ARG BASE_COMMIT=c59e83a1ffba63d709ea4847445845edd82085dc
RUN git checkout ${BASE_COMMIT}

# Set up the core package
WORKDIR /workspace/langchain/libs/core

# Install dependencies using uv
RUN uv sync --all-groups

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/langchain/libs/core
