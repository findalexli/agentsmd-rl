FROM golang:1.22

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone Hugo repo at base commit
ARG BASE_COMMIT=13a95b9c0167c832fe2babf961ac5cad22e3a1e4
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git && \
    cd hugo && \
    git checkout ${BASE_COMMIT}

# Allow Go to download newer toolchain if needed
ENV GOTOOLCHAIN=auto

# Install Go dependencies (pre-download for faster tests)
RUN cd /workspace/hugo && go mod download

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
