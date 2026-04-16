FROM golang:1.25-bookworm

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace/hugo

# Clone the Hugo repo at the base commit
# Using filter=blob:none for faster clone
ARG BASE_COMMIT=e8577771c3275d16b7d1b31cca5e9fd3ea517416
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    git checkout ${BASE_COMMIT}

# Download Go dependencies
RUN go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
