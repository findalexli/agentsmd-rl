FROM eclipse-temurin:17-jdk-jammy

# Install dependencies: git, python3, pip
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install bazelisk
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Set up workspace
WORKDIR /workspace

# Clone the selenium repo at base commit
RUN git clone --no-checkout https://github.com/SeleniumHQ/selenium.git /workspace/selenium \
    && cd /workspace/selenium \
    && git checkout 1303596bccafc9f39708d8ac61b52424c7d00394

WORKDIR /workspace/selenium

# Install pytest
RUN pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Create logs directory
RUN mkdir -p /logs/verifier
