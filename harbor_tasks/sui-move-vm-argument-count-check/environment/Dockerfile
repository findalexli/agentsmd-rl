FROM rust:1.85-slim

# Install Python and other dependencies needed for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pkg-config \
    libclang-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace/sui

# Clone the repo at base commit (shallow clone for faster download)
# Using filter=blob:none for partial clone to save space
RUN git init /workspace/sui && \
    cd /workspace/sui && \
    git remote add origin https://github.com/MystenLabs/sui.git && \
    git fetch --depth=1 origin 44e12d2c78cf6724a80fc06828bfa89b98c8de8f && \
    git checkout FETCH_HEAD

# Install Python packages for test runner
RUN pip3 install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-fetch dependencies to speed up builds
RUN cargo fetch -p move-vm-runtime 2>/dev/null || true

# Default command
CMD ["/bin/bash"]
