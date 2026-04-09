FROM rust:1.85-slim

# Install dependencies: git, python3, pip, curl
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt-get/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the sui repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=b62e4bf94eaaf96cb2d42b643ba92847bbf57be8
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git sui && \
    cd sui && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
