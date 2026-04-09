FROM python:3.12-slim

# Install system dependencies for Rust and Python testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    git \
    pkg-config \
    libssl-dev \
    rustc \
    cargo \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit
WORKDIR /workspace
ARG BASE_COMMIT=5e3503530862e1de135711cb68a70243bfed9acb
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git && \
    cd chroma && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/chroma

# Copy test files
COPY tests/ /workspace/tests/
RUN chmod +x /workspace/tests/test.sh

# Default command runs the test script
CMD ["/workspace/tests/test.sh"]
