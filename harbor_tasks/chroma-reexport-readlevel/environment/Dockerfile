FROM rust:1.85-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone chroma repo at base commit (shallow clone for speed)
ARG BASE_COMMIT
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git /workspace/chroma \
    && cd /workspace/chroma \
    && git checkout ${BASE_COMMIT}

# Set working directory
WORKDIR /workspace/chroma

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-fetch dependencies to speed up testing
RUN cd /workspace/chroma/rust/chroma && cargo fetch

# Copy test file
COPY test_outputs.py /workspace/test_outputs.py

# Default command
CMD ["bash"]
