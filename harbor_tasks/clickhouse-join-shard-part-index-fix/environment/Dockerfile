# ClickHouse task environment - lightweight version
# The PR fixes a bug in optimizeJoinByShards.cpp where part_index_in_query was incorrectly calculated

FROM python:3.12-slim

# Install minimal dependencies: git
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip install pytest

# Create directories and set up a minimal repo structure
# We'll mount the actual test files
WORKDIR /workspace

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# The actual ClickHouse repo will be mounted/cloned at runtime
WORKDIR /workspace/ClickHouse
