FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    wget \
    curl \
    ca-certificates \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Download the specific file from the base commit
RUN mkdir -p /workspace/ClickHouse/src/Storages/ObjectStorageQueue && \
    curl -sL "https://raw.githubusercontent.com/ClickHouse/ClickHouse/c71831a6b0df9e6b69eaba0e4cf83801c1fb3832/src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp" \
    -o /workspace/ClickHouse/src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp

# Pre-create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/ClickHouse

# Default command
CMD ["bash"]
