FROM rust:1.85-slim

# Install Python (needed by pytest runner) and git
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repo at base commit (shallow clone for speed)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git sui && \
    cd sui && \
    git checkout 2409c793c8f6092d665d28030cfc68967e5fc4dd

# Pre-download Rust dependencies for faster builds
WORKDIR /workspace/sui
RUN cargo fetch 2>/dev/null || true

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
