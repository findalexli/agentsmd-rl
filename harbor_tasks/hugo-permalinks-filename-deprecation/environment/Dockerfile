FROM golang:1.24-bookworm

# Install Python for test runner and bc for timing calculations
RUN apt-get update && apt-get install -y python3 python3-pip git bc && rm -rf /var/lib/apt/lists/*

# Enable GOTOOLCHAIN to automatically download newer Go versions
ENV GOTOOLCHAIN=auto

# Set up workspace
WORKDIR /workspace

# Clone Hugo repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=fa8658111f9c79b3f6381273fe822854a759fe1a
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    cd /workspace/hugo && \
    git checkout ${BASE_COMMIT}

# Install Go dependencies (Hugo doesn't use vendor/)
WORKDIR /workspace/hugo

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default to the hugo directory
WORKDIR /workspace/hugo
