FROM golang:1.23-bookworm

# Install Python and other tools needed for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Enable GOTOOLCHAIN to auto-download correct Go version
ENV GOTOOLCHAIN=auto

# Set up working directory
WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/pulumi/pulumi.git /workspace/pulumi && \
    cd /workspace/pulumi && \
    git checkout 40fd96368b6bab557b45747a4e4cb5a9082a7340

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set final working directory
WORKDIR /workspace/pulumi
