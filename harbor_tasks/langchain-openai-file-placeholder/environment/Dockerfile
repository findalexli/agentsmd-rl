FROM python:3.12-slim

# Install git, curl, make, and other build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the langchain repo with shallow depth for the base commit
# Using depth 500 to ensure we have enough history
ARG BASE_COMMIT=86238a775edc438add00836fb89d6879bbd8f1ed
RUN git clone --filter=blob:none --depth=500 https://github.com/langchain-ai/langchain.git langchain && \
    cd langchain && \
    git checkout ${BASE_COMMIT}

# Set working directory to the repo
WORKDIR /workspace/langchain

# Install uv for dependency management
RUN pip install uv

# Install only langchain-core dependencies (what we need for testing)
# We need to install the core library in editable mode
RUN cd libs/core && uv pip install --system -e ".[dev]"

# Install ruff for linting checks
RUN pip install ruff

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Set environment variables for Python
ENV PYTHONPATH=/workspace/langchain/libs/core:$PYTHONPATH
ENV PYTHONDONTWRITEBYTECODE=1
