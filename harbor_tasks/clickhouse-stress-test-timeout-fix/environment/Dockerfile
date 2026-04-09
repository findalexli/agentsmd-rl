FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    bash \
    git \
    shellcheck \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create workspace and logs directories
RUN mkdir -p /workspace/ClickHouse /logs/verifier

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse

# Checkout the base commit
WORKDIR /workspace/ClickHouse
RUN git checkout 0e2f4c6c1fef69f5c0ba46252d04b1cd4687b661

# Set working directory
WORKDIR /workspace/ClickHouse
