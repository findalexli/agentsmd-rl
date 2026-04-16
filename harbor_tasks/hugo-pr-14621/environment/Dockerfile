FROM golang:1.23-bookworm

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment for tests
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install pytest
ENV PATH="/opt/venv/bin:$PATH"

# Clone Hugo repo at base commit (parent of merge commit)
ARG BASE_COMMIT=59e0446fe5c7cb8080a3f0736c4453110b89f732
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    cd /workspace/hugo && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/hugo

# Download Go modules (for faster subsequent builds)
# Enable GOTOOLCHAIN to auto-download required Go version
ENV GOTOOLCHAIN=auto
RUN go mod download

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
