FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk (Bazel version manager)
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Clone the repository at base commit
WORKDIR /workspace
ARG REPO=selenium
ARG BASE_COMMIT=7beae82d3e1fbdcb30eb5165f8f4726a83c0fd26
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git ${REPO} \
    && cd ${REPO} \
    && git checkout ${BASE_COMMIT}

# Install Python dependencies for testing
RUN pip install --no-cache-dir pytest

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
