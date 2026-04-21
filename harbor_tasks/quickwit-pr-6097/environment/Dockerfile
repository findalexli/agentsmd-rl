FROM python:3.12-slim

WORKDIR /workspace

# Install Rust, Cargo, build essentials, and protobuf compiler
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Install rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable

# Add Cargo to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone the repository at the base commit
RUN git clone --depth=1 --filter=blob:none https://github.com/quickwit-oss/quickwit.git /workspace/quickwit
WORKDIR /workspace/quickwit
RUN git fetch origin e2d9623d1cb64cf0bc85f2a0f0dd858c42651d50 && git checkout e2d9623d1cb64cf0bc85f2a0f0dd858c42651d50

# Install pytest for running tests
RUN pip install --no-cache-dir pytest==8.3.4

WORKDIR /workspace

# Create directory for verifier logs
RUN mkdir -p /logs/verifier

# Default to running tests
CMD ["bash"]