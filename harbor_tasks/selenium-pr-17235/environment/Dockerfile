# Dockerfile for SeleniumHQ/selenium#17235
# Fix VNC caps not propagated for sessions without browserName

FROM eclipse-temurin:17-jdk-jammy

# Install Python for test harness, build tools, and utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk
RUN curl -L -o /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/download/v1.19.0/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

WORKDIR /workspace

# Clone repository at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout b1a7b8de7bf8c9889627914888adee44c01f925a

WORKDIR /workspace/selenium

# Pre-fetch Bazel dependencies for the specific test target
RUN bazel fetch //java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest || true

# Create logs directory
RUN mkdir -p /logs/verifier
