FROM eclipse-temurin:21-jdk

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Set up working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit
ARG BASE_COMMIT=7219edd11fe97666ceaf9ff4fc625d5c39d4a420
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout ${BASE_COMMIT}

# Pre-download Gradle wrapper dependencies (optional optimization)
WORKDIR /workspace/kotlin
RUN ./gradlew --version || true

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Default workdir for tests
WORKDIR /workspace/kotlin
