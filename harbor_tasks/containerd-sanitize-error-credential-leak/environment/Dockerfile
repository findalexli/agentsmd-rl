FROM golang:1.23-bookworm

# Install Python and pip for pytest
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone containerd repo at base commit
WORKDIR /workspace
ARG BASE_COMMIT=11eca1958537a47c43cd6b922f7242cb98196db7
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git && \
    cd containerd && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install Go dependencies
WORKDIR /workspace/containerd
RUN go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/containerd
