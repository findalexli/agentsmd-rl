FROM ubuntu:24.04

# Install required packages including Java
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    openjdk-21-jdk \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone Kotlin repository at base commit (shallow clone for efficiency)
# Using filter=blob:none to get tree without all file contents initially
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git kotlin

WORKDIR /workspace/kotlin

# Checkout the base commit
RUN git checkout 19feb3343bc36aa7d313df6f633cbf77eb8831bd

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-fetch gradle wrapper and common dependencies to speed up testing
RUN ./gradlew --version || true
