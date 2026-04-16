FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Create workspace
WORKDIR /workspace

# Clone langchain repo at base commit
# Base commit: ce21bf469d7493f4716bc30feb15a5b3f16ebe1e
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git && \
    cd langchain && \
    git fetch --depth=100 origin ce21bf469d7493f4716bc30feb15a5b3f16ebe1e && \
    git checkout ce21bf469d7493f4716bc30feb15a5b3f16ebe1e

# Set working directory to the core package
WORKDIR /workspace/langchain/libs/core

# Install dependencies using pip (uv sync has issues with the monorepo setup)
# Install pydantic first as it's the core dependency
RUN pip install --no-cache-dir \
    pydantic \
    pyyaml \
    pytest \
    langsmith \
    jsonpatch \
    orjson \
    packaging \
    typing-extensions

# Install the langchain-core package in editable mode
RUN pip install --no-cache-dir -e .

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment
ENV PYTHONPATH=/workspace/langchain/libs/core:$PYTHONPATH
