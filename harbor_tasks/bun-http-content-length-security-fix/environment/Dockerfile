# Bun HTTP security fix task
# PR #28838: Reject conflicting duplicate Content-Length headers
FROM oven/bun:1.2.4-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for test runner
RUN pip3 install pytest pyyaml --break-system-packages || pip3 install pytest pyyaml

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Clone the Bun repository at the base commit (pre-fix)
WORKDIR /workspace
ARG BASE_COMMIT=5b3ca83b84f90ccc9c71005db0ab9bd87850bc70
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 5b3ca83b84f90ccc9c71005db0ab9bd87850bc70 && \
    git checkout FETCH_HEAD \
    && git submodule update --init --recursive --depth=1 || true

WORKDIR /workspace/bun

# Set environment
ENV REPO=/workspace/bun
