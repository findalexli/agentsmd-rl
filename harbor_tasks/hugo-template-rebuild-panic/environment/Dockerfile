FROM golang:1.25-bookworm

# Install required tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for test running
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace/hugo

# Clone Hugo repository at base commit (before the fix)
ARG BASE_COMMIT=161d0d475773c5251ec00cc8848f1a174393155c
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    git checkout ${BASE_COMMIT}

# Build Hugo binary (standard edition, no CGO)
RUN CGO_ENABLED=0 go build -o /usr/local/bin/hugo .

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
