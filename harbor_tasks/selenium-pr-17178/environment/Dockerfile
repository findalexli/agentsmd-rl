# Selenium .NET BiDi EventDispatcher task environment
FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for test harness and basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    unzip \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install pytest
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pytest

# Install Bazelisk
RUN curl -fsSL https://github.com/bazelbuild/bazelisk/releases/download/v1.19.0/bazelisk-linux-amd64 -o /usr/local/bin/bazel \
    && chmod +x /usr/local/bin/bazel

# Clone Selenium repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout 41e422ae7922295d71929874f09f5e9957b91e54

WORKDIR /workspace/selenium

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
