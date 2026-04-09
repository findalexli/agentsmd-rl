FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install essential build dependencies for ClickHouse
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    llvm-18 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    ca-certificates \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest --break-system-packages

# Create workspace and logs directories
RUN mkdir -p /workspace/ClickHouse /logs/verifier

# Set working directory
WORKDIR /workspace/ClickHouse

# Clone the ClickHouse repository and checkout base commit
# Base commit: dae8318c5ed52baecd784a85a67c45d985b20d6a
# Use minimal clone - just the files needed for testing
RUN git init . && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=100 origin dae8318c5ed52baecd784a85a67c45d985b20d6a && \
    git checkout FETCH_HEAD && \
    rm -rf .git

# Default command
CMD ["/bin/bash"]
