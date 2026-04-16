FROM golang:1.24-bookworm

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone containerd repository at base commit
ARG BASE_COMMIT=1abba0c96162254eb85b3350aec4dbe2684a94ef
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git containerd && \
    cd containerd && \
    git checkout ${BASE_COMMIT}

# Install Go dependencies - use GOTOOLCHAIN to download newer Go if needed
WORKDIR /workspace/containerd
ENV GOTOOLCHAIN=auto
RUN go mod download

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV GOPATH=/go
ENV PATH=$PATH:$GOPATH/bin
WORKDIR /workspace/containerd
