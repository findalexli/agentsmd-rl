FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (parent of merge commit)
# Base commit: 475408fa620996e1958d18a0789ed5bf9fdee054
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git && \
    cd langchain && \
    git checkout 475408fa620996e1958d18a0789ed5bf9fdee054

WORKDIR /workspace/langchain

# Install langchain-core dependencies with uv
# The core package is in libs/core/
RUN cd libs/core && \
    uv pip install --system -e ".[dev]" || \
    pip install -e ".[dev]"

# Also install pytest and other test deps
RUN pip install pytest pytest-asyncio blockbuster pytest-mock syrupy

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Set environment
ENV PYTHONPATH=/workspace/langchain/libs/core:$PYTHONPATH
