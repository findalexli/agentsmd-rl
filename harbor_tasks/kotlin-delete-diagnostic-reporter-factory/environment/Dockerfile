FROM eclipse-temurin:17-jdk

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone Kotlin repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=3aaf150ccf7552462de7c2ad227ae049673ab11e
RUN git clone --filter=blob:none --depth=100 https://github.com/JetBrains/kotlin.git kotlin && \
    cd kotlin && \
    git checkout ${BASE_COMMIT}

# Pre-download Gradle wrapper and some dependencies to speed up tests
WORKDIR /workspace/kotlin
RUN ./gradlew --version || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/kotlin
