FROM python:3.12-slim

# Install Java, git, and other dependencies
RUN apt-get update && apt-get install -y \
    openjdk-21-jdk \
    git \
    curl \
    ca-certificates \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install Bazelisk (Bazel version manager)
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Create working directories
RUN mkdir -p /workspace/selenium /logs/verifier

# Clone the repository at base commit
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git /workspace/selenium \
    && cd /workspace/selenium \
    && git checkout b1a7b8de7bf8c9889627914888adee44c01f925a

# Install pytest for the test runner
RUN pip install pytest

WORKDIR /workspace/selenium
