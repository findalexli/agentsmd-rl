FROM golang:1.25-rc-bookworm

# Allow Go toolchain to download newer versions
ENV GOTOOLCHAIN=auto

# Install Python and pip for pytest
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone Hugo repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=d8ec0eeeaf2ff078565fddbbab5565a65b86346c
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    cd /workspace/hugo && \
    git checkout ${BASE_COMMIT}

# Install Go module dependencies
WORKDIR /workspace/hugo
RUN go mod download

# Pre-build to warm cache and verify setup
RUN go build -o /dev/null ./... 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/hugo
