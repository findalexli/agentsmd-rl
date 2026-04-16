FROM golang:1.23-bookworm

# Allow Go toolchain to auto-upgrade to required version
ENV GOTOOLCHAIN=auto

# Install Python and pytest for running tests
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace

# Clone prometheus at the base commit (parent of merge commit)
# Base commit: f99f3bb65d779dbaafe8b617c398b4f79b02e6d9
RUN git clone --filter=blob:none https://github.com/prometheus/prometheus.git /workspace/prometheus && \
    cd /workspace/prometheus && \
    git checkout f99f3bb65d779dbaafe8b617c398b4f79b02e6d9

# Create logs directory for verifier output
RUN mkdir -p /logs/verifier

WORKDIR /workspace/prometheus
