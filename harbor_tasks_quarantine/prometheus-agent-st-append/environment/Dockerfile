FROM golang:1.25-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    make \
    patch \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone prometheus repo at base commit (shallow clone for speed)
# Base commit: 788d122903baae36e823ec3b6c759aeb877ba1a7
RUN git clone --filter=blob:none https://github.com/prometheus/prometheus.git prometheus && \
    cd prometheus && \
    git checkout 788d122903baae36e823ec3b6c759aeb877ba1a7

# Install Python for pytest test runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/prometheus
