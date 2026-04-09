FROM rust:1.85-slim

# Install Python and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git sui && \
    cd sui && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/sui
