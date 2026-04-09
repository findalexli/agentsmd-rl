FROM golang:1.25-bookworm

# Install Python and required tools for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone containerd repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=3a2c003f946e1dbe3e11888465624ff3c231af84
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git /workspace/containerd && \
    cd /workspace/containerd && \
    git checkout ${BASE_COMMIT}

# Pre-download Go dependencies to speed up test execution
WORKDIR /workspace/containerd
RUN go mod download

# Default working directory for the task
WORKDIR /workspace/containerd
