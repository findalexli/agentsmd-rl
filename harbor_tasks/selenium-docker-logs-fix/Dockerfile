FROM openjdk:21-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y python3 python3-pip git curl && rm -rf /var/lib/apt/lists/*

# Install Bazelisk
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout 491207a87b89b2824d8ca976fa7cb46cce9325ea

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
