FROM python:3.12-slim

# Install git and other basic tools
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the lancedb repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=ad9648911494cc7bbac765a116463f831081c219
RUN git clone --filter=blob:none https://github.com/lancedb/lancedb.git && \
    cd lancedb && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies for the tests
WORKDIR /workspace/lancedb/python

# Install minimal dependencies needed for testing query.py
RUN pip install --no-cache-dir \
    pytest \
    pyarrow \
    numpy \
    pydantic \
    deprecation \
    typing_extensions

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the python package
WORKDIR /workspace/lancedb/python/python
