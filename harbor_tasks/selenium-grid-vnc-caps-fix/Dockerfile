FROM openjdk:21-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Setup virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip pytest pyyaml

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout b1a7b8de7bf8c9889627914888adee44c01f925a

# Ensure log directory exists
RUN mkdir -p /logs/verifier

# Install Bazelisk
RUN apt-get update && apt-get install -y curl && \
    curl -Lo /usr/local/bin/bazelisk https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 && \
    chmod +x /usr/local/bin/bazelisk && \
    ln -s /usr/local/bin/bazelisk /usr/local/bin/bazel

WORKDIR /workspace/selenium

# Pre-fetch some common dependencies
RUN bazel fetch //java/... 2>/dev/null || true

WORKDIR /workspace
