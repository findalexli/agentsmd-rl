FROM golang:1.24-bookworm

# Enable GOTOOLCHAIN to auto-upgrade Go version if needed
ENV GOTOOLCHAIN=auto

# Install Python and pytest for running tests
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pytest-timeout --break-system-packages

# Create required directories
RUN mkdir -p /logs/verifier /workspace/hugo

# Clone Hugo repo at base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git && \
    cd hugo && \
    git checkout b55d452e46e81369a65978459a0683efa484c11b

# Pre-download Go module dependencies for faster test runs
WORKDIR /workspace/hugo
RUN go mod download

# Default workdir for tests
WORKDIR /workspace/hugo
