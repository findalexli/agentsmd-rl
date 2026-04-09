FROM ruby:3.2-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Set up Python environment for pytest
RUN python3 -m pip install --break-system-packages pytest pyyaml

# Create required directories
RUN mkdir -p /workspace/selenium /logs/verifier

# Clone the selenium repo at base commit (shallow clone for speed)
WORKDIR /workspace
RUN git clone --depth=100 https://github.com/SeleniumHQ/selenium.git && \
    cd selenium && \
    git checkout 2fed1c09849431329f3e414479c627d652424f4e

WORKDIR /workspace/selenium
