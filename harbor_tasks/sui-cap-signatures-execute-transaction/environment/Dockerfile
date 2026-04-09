FROM rust:1.85-slim

# Install python3 for pytest
RUN apt-get update && apt-get install -y python3 python3-pip git pkg-config libclang-dev && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone sui repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=73efc3be4ccf819cc5dfb38c10d301396ad75c94
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/sui

# Pre-fetch dependencies to speed up builds
RUN cargo fetch

# Create logs directory
RUN mkdir -p /logs/verifier
