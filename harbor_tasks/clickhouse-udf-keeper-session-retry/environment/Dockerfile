# ClickHouse source code validation environment
# Minimal image - we only need to verify source code changes, not compile

FROM ubuntu:24.04

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python test dependencies
RUN pip3 install pytest pyyaml --break-system-packages

# Create workspace
WORKDIR /workspace

# Clone only the specific commit we need with minimal history
# Use single-branch and shallow clone to minimize disk usage
ARG BASE_COMMIT=ac01e7e5223a05f2a77ba74cdd949232d9648918
RUN git clone --depth=1 --single-branch --filter=blob:none \
    https://github.com/ClickHouse/ClickHouse.git clickhouse && \
    cd clickhouse && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/clickhouse

# Clean up git history to save space - we only need the working tree
RUN rm -rf .git/objects/pack/* .git/objects/info/*

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

# Verify Python and git are available
RUN python3 --version && git --version
