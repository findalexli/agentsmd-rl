# Dockerfile for electron-window-size-constraints task
# Verifies C++ code changes in shell/browser/native_window.cc

FROM python:3.12-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    gnupg \
    build-essential \
    clang-format \
    && rm -rf /var/lib/apt/lists/*

# Create workspace and logs directories
RUN mkdir -p /workspace/electron /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone electron repo at base commit
# Using --filter=blob:none for partial clone to save time/space
RUN git clone --filter=blob:none https://github.com/electron/electron.git /workspace/electron && \
    cd /workspace/electron && \
    git checkout a0f042f8d3e1123e7112a868954ab3c7c843f0b7

# Install Python dependencies for testing
RUN pip install --no-cache-dir pytest pyyaml

# Copy task files (using the fixed versions)
COPY tests/test_outputs.py /workspace/tests/
COPY solution/solve.sh /workspace/solution/
COPY task.toml /workspace/

# Make solve.sh executable
RUN chmod +x /workspace/solution/solve.sh

# Set environment
ENV PYTHONPATH=/workspace
ENV REPO_PATH=/workspace/electron
