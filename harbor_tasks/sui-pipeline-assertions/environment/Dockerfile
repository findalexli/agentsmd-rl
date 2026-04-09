FROM rust:1.85-slim

# Install Python for the test runner and build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    libclang-dev \
    clang \
    llvm-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable for bindgen to find libclang
ENV LIBCLANG_PATH=/usr/lib/llvm-14/lib

# Set up a virtual environment for pytest
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install pytest

# Set up working directory
WORKDIR /workspace/sui

# Clone the repo at the base commit (sparse clone for speed)
ARG BASE_COMMIT=f8024baa75086db5a440d98247ecfd3d1ee90c73
RUN git clone --filter=blob:none --no-checkout https://github.com/MystenLabs/sui.git . && \
    git checkout ${BASE_COMMIT}

# Create log directory
RUN mkdir -p /logs/verifier

# Keep container running
CMD ["bash"]
