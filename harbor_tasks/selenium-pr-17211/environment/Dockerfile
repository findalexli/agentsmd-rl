# Selenium Grid Router read timeout task
FROM eclipse-temurin:17-jdk-jammy

# Install system dependencies including build tools for Bazel
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    python3 \
    python3-pip \
    unzip \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk (which manages Bazel versions)
RUN curl -fsSL https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64 \
    -o /usr/local/bin/bazel && chmod +x /usr/local/bin/bazel

# Clone Selenium repository with filter for faster clone
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium

# Checkout the base commit (parent of merge commit)
WORKDIR /workspace/selenium
RUN git checkout 874358a3c4b503095669565e1ba26414439ec6a3

# Pre-fetch Bazel dependencies to speed up builds
# This will fail on first run but primes the cache
RUN bazel version || true
RUN bazel fetch //java/src/org/openqa/selenium/grid/router/... || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
