FROM golang:1.24-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    make \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for pytest
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip pytest

# Clone the containerd repository at base commit
WORKDIR /workspace
ARG REPO_SHORT=containerd
ARG BASE_COMMIT=d1c2ba148c50081b4fc7f074d34d78aaad3ef258

RUN git clone --filter=blob:none https://github.com/containerd/containerd.git ${REPO_SHORT} && \
    cd ${REPO_SHORT} && \
    git checkout ${BASE_COMMIT}

# Install Go dependencies for testing
WORKDIR /workspace/containerd
RUN go mod download || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory
WORKDIR /workspace/containerd
