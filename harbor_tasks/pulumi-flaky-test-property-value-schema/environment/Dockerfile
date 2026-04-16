FROM golang:1.24-bookworm

# Enable automatic toolchain selection
ENV GOTOOLCHAIN=auto

# Install python3 for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install --break-system-packages pytest

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repository at base commit (shallow clone for speed)
WORKDIR /workspace
ARG BASE_COMMIT=e7a8c6babcdd6a6b97d288c3c82b61845a286bbd
RUN git clone --filter=blob:none --depth=100 https://github.com/pulumi/pulumi.git && \
    cd pulumi && \
    git checkout ${BASE_COMMIT}

# Let tests download dependencies as needed
WORKDIR /workspace/pulumi
