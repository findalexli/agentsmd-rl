FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (use virtual environment to avoid system package conflicts)
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install pytest pyyaml && \
    ln -s /opt/venv/bin/pytest /usr/local/bin/pytest

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at base commit
ARG BASE_COMMIT=9ae4df2ec0416c7b051b128a8a8d3bd23efbfe1f
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git fetch --depth=50 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Build dependencies first for better caching
WORKDIR /workspace/sui/external-crates/move/crates/language-benchmarks
RUN cargo fetch

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
