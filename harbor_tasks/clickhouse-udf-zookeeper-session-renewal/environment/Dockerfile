FROM python:3.12-slim

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip install pytest pyyaml

# Create workspace directory
WORKDIR /workspace

# Copy the target file at base commit (before the fix)
RUN mkdir -p /workspace/ClickHouse/src/Functions/UserDefined
COPY UserDefinedSQLObjectsZooKeeperStorage.cpp /workspace/ClickHouse/src/Functions/UserDefined/

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
