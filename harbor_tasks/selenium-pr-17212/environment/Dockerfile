# Selenium .NET BiDi benchmark task
FROM mcr.microsoft.com/dotnet/sdk:8.0-bookworm-slim

# Install python3 for pytest runner and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk
RUN curl -fsSL https://github.com/bazelbuild/bazelisk/releases/download/v1.20.0/bazelisk-linux-amd64 \
    -o /usr/local/bin/bazel && chmod +x /usr/local/bin/bazel

WORKDIR /workspace

# Clone repository at base commit (sparse checkout for .NET only)
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout 1dc4a61843346508c0464bab596b867e7e389966

WORKDIR /workspace/selenium

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
