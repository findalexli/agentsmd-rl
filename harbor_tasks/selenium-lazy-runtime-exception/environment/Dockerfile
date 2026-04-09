FROM python:3.12-slim

# Install Java, curl, git, build tools, and other build essentials
RUN apt-get update && apt-get install -y \
    curl \
    git \
    openjdk-21-jdk \
    build-essential \
    gcc \
    g++ \
    ca-certificates \
    gnupg \
    unzip \
    zip \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk (Bazel version manager)
RUN curl -Lo /usr/local/bin/bazelisk https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazelisk \
    && ln -s /usr/local/bin/bazelisk /usr/local/bin/bazel

# Set up environment
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Clone the Selenium repository at base commit (before the fix)
WORKDIR /workspace
ARG BASE_COMMIT=4bb23f484eec6f986b563fb3146cb64dcbcc0187
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/selenium

# Pre-fetch Bazel to cache the version
RUN bazel --version

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
