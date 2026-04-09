FROM python:3.12-slim

# Install git and basic dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone selenium repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=39436b0c1eabbed5489148b98a36302d77feed9e
RUN git clone --depth=100 --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies for testing
RUN pip install --no-cache-dir pytest mypy

# Create log directory
RUN mkdir -p /logs/verifier

# Set working directory to the Python package
WORKDIR /workspace/selenium/py

# Pre-install package dependencies to speed up tests
RUN pip install --no-cache-dir -e . 2>/dev/null || true
