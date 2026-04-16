FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/apache/superset.git && \
    cd superset && \
    git checkout 38fdfb4ca2e4fbca5c308898d9c1d5f58e2e7302

WORKDIR /workspace/superset

# Install Python dependencies
RUN pip install --no-cache-dir \
    pydantic>=2.0 \
    pytest \
    pytest-mock \
    typing-extensions

# Pre-install any MCP-related dependencies that might be needed
RUN pip install --no-cache-dir fastmcp 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment variables
ENV PYTHONPATH=/workspace/superset:$PYTHONPATH
