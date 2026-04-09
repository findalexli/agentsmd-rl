FROM eclipse-temurin:21-jdk

# Install dependencies: git, python3, curl, unzip
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone Kotlin repository at base commit (shallow clone for speed)
# Using filter=blob:none for partial clone to save space while preserving history
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout 7730271d0f5754fdffedf0199ab34b405dc746b0

# Pre-download Gradle wrapper dependencies to speed up subsequent builds
WORKDIR /workspace/kotlin
RUN ./gradlew --version || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory for running tests
WORKDIR /workspace/kotlin
