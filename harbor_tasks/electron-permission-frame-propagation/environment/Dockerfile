FROM python:3.12-slim

# Install required tools for verification
RUN apt-get update && apt-get install -y \
    git \
    clang-format \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest and dependencies
RUN pip install pytest pyyaml

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone electron repository at base commit
# Using --filter=blob:none to avoid downloading full blob history
RUN git clone --filter=blob:none https://github.com/electron/electron.git /workspace/electron

WORKDIR /workspace/electron

# Checkout the base commit (parent of merge commit)
RUN git checkout 821b738db0a64c863e8371e7141564cef70d56b8

# Set working directory
WORKDIR /workspace
