# Electron dock_state validation task
FROM node:22-slim

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    clang \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone Electron at the base commit (parent of merge commit)
# Using shallow clone with filter for efficiency
RUN git clone --filter=blob:none --depth=100 \
    https://github.com/electron/electron.git electron

WORKDIR /workspace/electron

# Checkout base commit (before the fix)
RUN git checkout 92892ca4815cf8c781e72a1b8ee717917992cc18

# Install Python dependencies for testing
RUN pip3 install pytest pyyaml --break-system-packages || pip3 install pytest pyyaml

# Create logs directory
RUN mkdir -p /logs/verifier

# Copy test files
COPY tests/ /workspace/task/tests/

# Default command
CMD ["/bin/bash"]
