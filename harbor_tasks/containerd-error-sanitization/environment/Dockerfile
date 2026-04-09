FROM golang:1.23-bookworm

# Install Python for test runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone containerd repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=11eca1958537a47c43cd6b922f7242cb98196db7
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git /workspace/containerd && \
    cd /workspace/containerd && \
    git checkout ${BASE_COMMIT}

# Pre-download Go module dependencies to speed up testing
RUN cd /workspace/containerd && go mod download
