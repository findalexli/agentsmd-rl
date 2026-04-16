FROM golang:1.24-bookworm

# Install Python for pytest
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Enable Go toolchain auto-download to get the required Go version
ENV GOTOOLCHAIN=auto

# Set working directory
WORKDIR /workspace/hugo

# Clone the Hugo repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=0c013c2326be1bbebba9a9f89d27072074fc6cc4
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    git checkout ${BASE_COMMIT}

# Pre-download Go modules (this layer is cacheable, GOTOOLCHAIN will download required Go version)
RUN go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
