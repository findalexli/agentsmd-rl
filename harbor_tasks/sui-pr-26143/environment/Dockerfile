FROM rust:1.85-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit with shallow depth for this task
RUN git clone --depth=100 --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git fetch --depth=100 origin f620dfc7c8d05e828e8f63bc5466b10ed4979e6d && \
    git checkout f620dfc7c8d05e828e8f63bc5466b10ed4979e6d

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
