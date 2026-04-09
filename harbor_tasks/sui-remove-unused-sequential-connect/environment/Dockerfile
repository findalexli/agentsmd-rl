FROM rust:1.85-slim

# Install dependencies for building
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at the base commit (before the fix)
WORKDIR /workspace
ARG BASE_COMMIT=3ac6f119a3ce41fccb9df0293a51e40ed6fadae3
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
