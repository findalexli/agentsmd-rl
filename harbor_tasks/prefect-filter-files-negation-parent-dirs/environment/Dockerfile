FROM python:3.12-slim

# Install git, patch and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace

# Clone the prefect repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=45186a33d5e3f0f66383f27b984c25e3a29e6302
RUN git clone --filter=blob:none --depth=50 https://github.com/prefecthq/prefect.git && \
    cd prefect && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies needed for testing
# Pin exact versions for reproducibility
RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-asyncio==0.21.2 \
    pathspec==0.12.1 \
    fsspec==2024.6.0

# Ensure the prefect package is importable
ENV PYTHONPATH=/workspace/prefect/src:$PYTHONPATH

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/prefect
