FROM python:3.12-slim

# Install git, patch and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone langchain repo at base commit (shallow clone for efficiency)
# Base commit: c9f51aef85e02fbaadcd5c6c37cf4ef01a49f86e
RUN git clone --filter=blob:none --depth=1000 https://github.com/langchain-ai/langchain.git langchain \
    && cd langchain \
    && git checkout c9f51aef85e02fbaadcd5c6c37cf4ef01a49f86e

# Install langchain-core in editable mode with minimal deps
WORKDIR /workspace/langchain/libs/core
RUN pip install --no-cache-dir -e .

# Install pytest and test dependencies from pyproject.toml test group
RUN pip install --no-cache-dir pytest pytest-mock blockbuster freezegun syrupy pytest-asyncio responses pytest-socket numpy

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Reset workdir to langchain root for tests
WORKDIR /workspace/langchain
