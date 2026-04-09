FROM ubuntu:24.04

# Install Python and basic tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Clone ClickHouse repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse

WORKDIR /workspace/ClickHouse
RUN git checkout 9893080d285656b1f90153260f95a675e002326b

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-install Python dependencies for testing
RUN pip3 install pyyaml --break-system-packages 2>/dev/null || pip3 install pyyaml
