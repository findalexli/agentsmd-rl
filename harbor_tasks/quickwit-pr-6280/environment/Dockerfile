FROM rust:1.85-slim

# Install python3 and pip for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone repository at the PR's base commit
RUN git clone --filter=blob:none https://github.com/quickwit-oss/quickwit.git /workspace/quickwit
WORKDIR /workspace/quickwit
RUN git checkout 469c60695b6c010d2ad4df4b5098b4db181c1059

# Install Python test dependencies
RUN pip install --no-cache-dir --break-system-packages pytest==8.3.4

# Default command
CMD ["bash"]