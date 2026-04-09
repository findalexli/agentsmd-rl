# Use the official ClickHouse binary builder image which has all dependencies
FROM clickhouse/binary-builder:latest

# Install Python for test runner and git for applying patches
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /workspace/ClickHouse /logs/verifier

WORKDIR /workspace/ClickHouse

# Default command keeps container running for test execution
CMD ["/bin/bash"]
