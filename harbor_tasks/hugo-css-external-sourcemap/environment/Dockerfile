# Hugo at this commit requires Go 1.24+
FROM golang:1.24-bookworm

# Install Python and pip (required by test harness)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone Hugo repo at base commit
WORKDIR /workspace
ARG BASE_COMMIT=a7cbcf15f0c5ef04b45350390e00e584e4d635b9
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git && \
    cd hugo && \
    git checkout ${BASE_COMMIT}

# Pre-download Go module dependencies (Hugo requires Go 1.25, use GOTOOLCHAIN=auto)
WORKDIR /workspace/hugo
ENV GOTOOLCHAIN=auto
RUN go mod download || echo "go mod download failed, will retry at test time"

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory
WORKDIR /workspace/hugo
