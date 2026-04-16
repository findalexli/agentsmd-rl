FROM python:3.12-slim

# Install git and other basic tools
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip install pytest

# Create workspace
WORKDIR /workspace

# Clone Bun repo at base commit (shallow clone for speed)
# This is a large repo, so we use filter=blob:none
RUN git clone --filter=blob:none --no-checkout https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git sparse-checkout init --cone && \
    git sparse-checkout set src/CLAUDE.md src/linker.zig src/logger.zig src/s3/credentials.zig && \
    git checkout 9a72bbfae2d086779739de54043a8e8bbd7ee9ed

# Create logs directory for test output
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/bun
