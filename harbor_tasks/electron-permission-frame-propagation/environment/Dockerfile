FROM python:3.12-slim

# Install required tools for verification
RUN apt-get update && apt-get install -y \
    git \
    clang-format \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest and dependencies
RUN pip install pytest pyyaml cpplint --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone electron repository efficiently with shallow depth
RUN git clone --depth=1 https://github.com/electron/electron.git /workspace/electron

WORKDIR /workspace/electron

# Fetch the specific base commit
RUN git fetch --depth=1 origin 821b738db0a64c863e8371e7141564cef70d56b8 \
    && git checkout FETCH_HEAD

# Set working directory
WORKDIR /workspace
