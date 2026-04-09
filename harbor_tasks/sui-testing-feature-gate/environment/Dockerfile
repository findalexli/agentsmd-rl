FROM rust:1.85-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the sui repository at base commit (shallow clone for speed)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 715582d4e58d46aa7d7a5e7b153b0e9c99978f9e

WORKDIR /workspace/sui
