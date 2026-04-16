FROM golang:1.23.4-bookworm

# Install Python and patch for test runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3=3.11.2-1+b1 \
    python3-pip=23.0.1+dfsg-1 \
    patch=2.7.6-7 \
    && rm -rf /var/lib/apt/lists/*

# Install pytest with pinned version
RUN pip3 install --break-system-packages pytest==8.3.4 --no-cache-dir

# Set working directory
WORKDIR /workspace/goose

# Clone the repo at base commit (will be overridden at runtime, but for caching)
ARG BASE_COMMIT=383286a33bba089cf05f6ffbc73836a81f355569
RUN git clone --filter=blob:none https://github.com/goose-lang/goose.git . && \
    git checkout ${BASE_COMMIT}

# Install Go dependencies
RUN go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
