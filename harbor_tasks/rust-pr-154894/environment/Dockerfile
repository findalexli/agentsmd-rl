FROM rustlang/rust:nightly-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace/rust

# Clone the rust repo at the base commit
# Use depth=1 and filter=blob:none to keep image size manageable
RUN git clone --filter=blob:none --depth=1 \
    https://github.com/rust-lang/rust.git . \
    && git fetch --depth=1 origin 906ca7ff5e1f01cdf59388574b4822365bffabea \
    && git checkout 906ca7ff5e1f01cdf59388574b4822365bffabea

# Install Python packages for testing
RUN pip3 install pytest --break-system-packages || pip3 install pytest

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
