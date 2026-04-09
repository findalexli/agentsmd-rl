FROM golang:1.23-bookworm

# Install Python and pytest (needed by test harness)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /workspace /logs/verifier

# Clone containerd repo at base commit
ARG REPO=containerd/containerd
ARG BASE_COMMIT=24032046138752ae363f90a697095d80ed3b778a

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/${REPO}.git containerd && \
    cd containerd && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/containerd

# Verify the repo is at the right commit
RUN git log --oneline -1

# Set environment
ENV GO111MODULE=on
ENV GOPROXY=https://proxy.golang.org,direct
