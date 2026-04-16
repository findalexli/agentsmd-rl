FROM golang:1.25

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace/pulumi

# Clone the repository at base commit with depth limit
ARG BASE_COMMIT=310f36beb5c3f5e8e920fc8af22d4da7804e5997
RUN git clone --depth=1000 https://github.com/pulumi/pulumi.git /workspace/pulumi && \
    git checkout ${BASE_COMMIT}

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
