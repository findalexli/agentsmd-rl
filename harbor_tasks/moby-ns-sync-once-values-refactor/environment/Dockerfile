FROM golang:1.24-bookworm

# Install Python for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel pytest

# Clone the repository at base commit
ARG BASE_COMMIT=a78d0a29777dc83d83eda80276bb847fb30f6b13
RUN git clone --filter=blob:none https://github.com/moby/moby.git /workspace/moby \
    && cd /workspace/moby \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/moby

# Allow Go to automatically download correct toolchain version
ENV GOTOOLCHAIN=auto

# Pre-download Go dependencies
RUN go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
