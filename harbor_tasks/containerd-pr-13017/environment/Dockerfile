# Go-based image for containerd
FROM golang:1.24-bookworm

# Install Python for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install pytest pyyaml

# Clone containerd at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git containerd
WORKDIR /workspace/containerd

# Checkout the base commit (parent of merge)
RUN git checkout 18201e7d52037a8a9657a2764ef63f60ec556e37

# Use GOTOOLCHAIN to get the required Go version automatically
ENV GOTOOLCHAIN=auto
RUN go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory
WORKDIR /workspace/containerd
