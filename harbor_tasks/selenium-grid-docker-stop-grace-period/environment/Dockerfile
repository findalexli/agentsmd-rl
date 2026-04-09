FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install dependencies: Java, Python (for pytest), curl, git, and build tools
RUN apt-get update && apt-get install -y \
    openjdk-21-jdk \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    git \
    build-essential \
    unzip \
    zip \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk (manages Bazel versions)
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Set up Python environment for pytest
RUN python3 -m pip install --break-system-packages pytest

# Clone Selenium repo at base commit
WORKDIR /workspace
ARG BASE_COMMIT=fbe388118cff80484638b724aaec3ee86c6eb0cd
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium

WORKDIR /workspace/selenium
RUN git fetch --depth=1 origin ${BASE_COMMIT} && git checkout ${BASE_COMMIT}

# Create logs directory
RUN mkdir -p /logs/verifier

# Pre-fetch some Bazel dependencies to speed up tests
RUN bazel fetch //java/src/org/openqa/selenium/grid/node/docker/... 2>/dev/null || true
