FROM python:3.12-slim

WORKDIR /workspace

# Install build dependencies and git
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    gcc \
    g++ \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (needed for building lancedb Python bindings)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone the lancedb repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=2d60ea693870ccc89dfe5ac20ee7c1b8dedee835
RUN git clone --filter=blob:none https://github.com/lancedb/lancedb.git /workspace/lancedb && \
    cd /workspace/lancedb && \
    git checkout ${BASE_COMMIT}

# Set working directory to the Python package
WORKDIR /workspace/lancedb/python

# Install Python dependencies (pre-built wheels where possible)
RUN pip install --no-cache-dir \
    pytest \
    pyarrow \
    numpy \
    pylance \
    lancedb || true

# Try to install the package in development mode (may fail without full Rust build)
# We'll make the tests work with just the Python code
RUN pip install -e . --no-build-isolation 2>/dev/null || \
    pip install lancedb --no-cache-dir || \
    echo "Will use pip install lancedb in solve.sh"

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variables
ENV PYTHONPATH=/workspace/lancedb/python/python:$PYTHONPATH

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
