FROM golang:1.24-bookworm

# Install Python and build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pkg-config \
    libnftables-dev \
    libbtrfs-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip

# Install pytest
RUN pip install pytest

# Create logs directory
RUN mkdir -p /logs/verifier

# Allow Go toolchain to auto-download newer versions
ENV GOTOOLCHAIN=auto

# Set working directory
WORKDIR /workspace

# Clone the repo at the base commit
ARG REPO=moby/moby
ARG BASE_COMMIT=2265448f5ddc318f3410a611db331ca3eb1d5c9d

RUN git clone --filter=blob:none https://github.com/${REPO}.git moby && \
    cd moby && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/moby

# Pre-download Go toolchain and cache build dependencies
RUN go version && go mod download
RUN timeout 300 go build ./daemon/internal/builder-next/... || true
