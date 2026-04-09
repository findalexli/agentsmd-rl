FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    openjdk-17-jdk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Clone the Kotlin repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout a304b4b5c79aa22c62ab5410caccaeb3a05c276a

# Pre-download Gradle wrapper and dependencies
WORKDIR /workspace/kotlin
RUN ./gradlew --version 2>/dev/null || true

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
