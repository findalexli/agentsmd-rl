FROM golang:1.25-rc-bookworm

# Enable toolchain for automatic Go version management
ENV GOTOOLCHAIN=auto

# Install Python and pytest for running tests
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit (before the fix)
# Using --filter=blob:none for faster clone
ARG BASE_COMMIT=1906c9877fbe7d33d4bd220e9851c719e1b43156
RUN git clone --filter=blob:none https://github.com/prometheus/prometheus.git /workspace/prometheus && \
    cd /workspace/prometheus && \
    git checkout ${BASE_COMMIT}

# Download Go dependencies
WORKDIR /workspace/prometheus
RUN go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
