FROM rust:1.85-slim

# Install system dependencies and Python for pytest
RUN apt-get update && apt-get install -y \
    git \
    curl \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at base commit
# Using --filter=blob:none for faster shallow clone
ARG BASE_COMMIT=89286c8e52b8b358b3bd895e40ec4ee2f991c742
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout ${BASE_COMMIT}

# Pre-download Rust dependencies to speed up subsequent builds
RUN cd sui && \
    cargo fetch --target x86_64-unknown-linux-gnu

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
