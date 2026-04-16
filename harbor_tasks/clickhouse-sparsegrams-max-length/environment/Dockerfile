FROM clickhouse/clickhouse-server:head

USER root

# Install Python, git, and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
RUN mkdir -p /workspace/clickhouse /logs/verifier

# Clone the ClickHouse repository at the base commit
# The sparseGrams fix is in the tokenizer implementation
# Use shallow clone with specific revision to save space
RUN cd /workspace && \
    git clone --depth=1 https://github.com/ClickHouse/ClickHouse.git clickhouse && \
    cd clickhouse && \
    git fetch --depth=1 origin 64b0a83ca8c950b0efa6a5972ec0f1ce3d622fd6 && \
    git checkout 64b0a83ca8c950b0efa6a5972ec0f1ce3d622fd6

WORKDIR /workspace/clickhouse
