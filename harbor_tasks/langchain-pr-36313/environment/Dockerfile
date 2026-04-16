FROM python:3.12-slim

# Install git, curl, and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repo at the base commit (with history for patch application)
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git langchain && \
    cd langchain && \
    git checkout 03515881176fddba919e3592e0a41cbc9806fdb8

WORKDIR /workspace/langchain

# Install langchain-core first (dependency)
RUN pip install -e libs/core

# Install langchain-text-splitters (dependency)
RUN pip install -e libs/text-splitters

# Install langchain-tests (needed for conftest)
RUN pip install -e libs/standard-tests

# Install langchain-openai (needed for tests)
RUN pip install -e libs/partners/openai

# Install langchain_v1 package
RUN pip install -e libs/langchain_v1

# Install test dependencies
RUN pip install pytest pytest-asyncio pytest-mock blockbuster syrupy ruff mypy

# Create logs directory
RUN mkdir -p /logs/verifier

# Keep container running for task execution
CMD ["sleep", "infinity"]
