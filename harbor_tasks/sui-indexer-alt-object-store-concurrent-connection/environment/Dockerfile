FROM rust:1.85-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace/sui

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=ffbf699bc89e0d16fbcdefdd9d459b1ca0ddb88a
RUN git clone --depth=100 https://github.com/MystenLabs/sui.git . && \
    git checkout ${BASE_COMMIT}

# Create log directory
RUN mkdir -p /logs/verifier

# Pre-fetch dependencies to speed up builds
RUN cargo fetch -p sui-indexer-alt-object-store 2>/dev/null || true

# Default command
CMD ["bash"]
