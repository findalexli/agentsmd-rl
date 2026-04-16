# Kotlin repository with Swift support for testing Swift Export
FROM swift:6.0-jammy

# Install dependencies for Kotlin/Gradle build system and Python
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    python3 \
    python3-pip \
    python3-venv \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install --upgrade pip setuptools wheel

# Create working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit (shallow clone for speed)
# Using filter=blob:none to get history without all blobs
ARG BASE_COMMIT=715bf60a9a2580d55253eb3bfebcd9be5e27a2aa
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git checkout ${BASE_COMMIT}

# Pre-install pytest in a virtual environment for the test harness
RUN python3 -m venv /opt/test-venv && \
    /opt/test-venv/bin/pip install pytest && \
    ln -sf /opt/test-venv/bin/pytest /usr/local/bin/pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
