FROM python:3.12-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the langchain repo at base commit
ARG BASE_COMMIT=e89afedfecad9b49bae977130f28995b064dd0a2
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git && \
    cd langchain && \
    git checkout ${BASE_COMMIT}

# Install langchain-core dependencies
WORKDIR /workspace/langchain/libs/core

# Install the package in development mode with all dependencies
RUN pip install -e . pytest

# Install ruff for linting
RUN pip install ruff

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/langchain
