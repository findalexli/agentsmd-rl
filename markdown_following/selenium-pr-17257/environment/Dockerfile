# Selenium Java - OSGi Resource Loading Fix
FROM eclipse-temurin:17-jdk-jammy

# Install Python3, git, patch, and build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    curl \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk (Bazel version manager)
RUN curl -fsSL https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64 -o /usr/local/bin/bazel \
    && chmod +x /usr/local/bin/bazel

# Clone Selenium repo at base commit
WORKDIR /workspace
RUN git init /workspace/selenium && \
    cd /workspace/selenium && \
    git remote add origin https://github.com/SeleniumHQ/selenium.git && \
    git fetch --depth=1 origin 36fc8f9b7bdedeba3884fadc232aec76fcd044c1 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/selenium

# Create logs directory
RUN mkdir -p /logs/verifier

# Set Java environment
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"
