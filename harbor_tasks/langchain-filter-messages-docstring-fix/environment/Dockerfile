FROM python:3.12-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the langchain repo at base commit
ARG BASE_COMMIT=e89afedfecad9b49bae977130f28995b064dd0a2
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/langchain-ai/langchain.git && \
    git fetch --depth=1 origin e89afedfecad9b49bae977130f28995b064dd0a2 && \
    git checkout FETCH_HEAD

# Install langchain-core dependencies
WORKDIR /workspace/langchain/libs/core

# Install the package in development mode with all dependencies
RUN pip install -e . pytest

# Install ruff for linting
RUN pip install ruff

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/langchain
