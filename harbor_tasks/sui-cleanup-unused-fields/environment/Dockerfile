FROM rust:1.85-slim

# Install system dependencies and Python for test runner
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest --break-system-packages

# Clone the Sui repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git sui && \
    cd sui && \
    git checkout 5ce3eba9d21aea6f051be3c3306078d2bc572c41

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
