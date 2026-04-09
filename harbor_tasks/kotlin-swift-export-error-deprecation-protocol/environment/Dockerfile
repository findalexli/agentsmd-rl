FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    unzip \
    default-jdk \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for test runner
RUN pip install pytest requests

# Clone Kotlin repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout 933370d290eb76fda562b41a7491362ed110574d

# Pre-download Gradle wrapper and basic dependencies
WORKDIR /workspace/kotlin
RUN ./gradlew --version 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
