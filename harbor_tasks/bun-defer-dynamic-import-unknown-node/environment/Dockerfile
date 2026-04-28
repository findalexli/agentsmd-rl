FROM python:3.12-slim

# Install git and tools needed for bun download
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun (v1.3.12 includes the fix from PR #26981, merged 2026-02-12)
# This version is needed to run the regression test that exercises the deferred
# dynamic import behavior at runtime via Bun.spawn subprocesses.
RUN curl -fsSLo /tmp/bun.zip \
    "https://github.com/oven-sh/bun/releases/download/bun-v1.3.12/bun-linux-x64.zip" && \
    unzip -o /tmp/bun.zip -d /usr/local/bin && \
    mv /usr/local/bin/bun-linux-x64/bun /usr/local/bin/bun && \
    rm -rf /usr/local/bin/bun-linux-x64 /tmp/bun.zip && \
    chmod +x /usr/local/bin/bun

# Install pytest
RUN pip install pytest

# Create workspace
WORKDIR /workspace

# Clone Bun repo at base commit (shallow clone for speed)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 9a72bbfae2d086779739de54043a8e8bbd7ee9ed && \
    git checkout FETCH_HEAD

# Create logs directory for test output
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/bun
