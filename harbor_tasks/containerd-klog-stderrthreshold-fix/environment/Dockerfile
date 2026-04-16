FROM golang:1.24-bookworm

# Install python3 and pytest (needed by test harness)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest --break-system-packages

# Set up working directory
WORKDIR /workspace

# Enable automatic toolchain selection
ENV GOTOOLCHAIN=auto

# Clone containerd repo at the base commit
ARG REPO=containerd/containerd
ARG BASE_COMMIT=38dafd778ea487dc6972c7caf10e1dc91d610e91
RUN git clone --filter=blob:none https://github.com/${REPO}.git containerd && \
    cd containerd && \
    git checkout ${BASE_COMMIT}

# Download Go modules
WORKDIR /workspace/containerd
RUN go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/containerd
