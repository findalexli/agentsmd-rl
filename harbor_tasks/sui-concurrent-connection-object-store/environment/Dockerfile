FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt-get/lists/*

# Install Python dependencies for pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the repo at base commit (using filter for efficiency)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout ffbf699bc89e0d16fbcdefdd9d459b1ca0ddb88a

# Pre-download dependencies to speed up builds
WORKDIR /workspace/sui
RUN cargo fetch

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
