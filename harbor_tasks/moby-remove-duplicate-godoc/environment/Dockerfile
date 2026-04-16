FROM golang:1.24-bookworm

# Install Python and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for testing
RUN pip3 install pyyaml --break-system-packages

# Set up Go toolchain to auto-download newer versions
ENV GOTOOLCHAIN=auto

# Set up working directory
WORKDIR /workspace/moby

# Clone the repository at the base commit
# Base commit: e2171f609d8b134f799885480fdb362bdd7b7b12
RUN git clone --filter=blob:none https://github.com/moby/moby.git /workspace/moby && \
    git checkout e2171f609d8b134f799885480fdb362bdd7b7b12

# Install golangci-lint for linting verification
RUN go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
