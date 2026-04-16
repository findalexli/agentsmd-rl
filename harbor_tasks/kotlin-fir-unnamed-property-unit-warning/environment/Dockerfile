FROM eclipse-temurin:21-jdk

# Install dependencies: git, python3, curl
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install specific Python packages for testing
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit
# Using shallow clone for faster download
RUN git clone --depth 100 --filter=blob:none https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git checkout 28b3f9991abde6c7bac4df4bd3aa9a8a8c07f100

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-download Gradle wrapper and some dependencies for faster test runs
WORKDIR /workspace/kotlin
RUN ./gradlew --version 2>/dev/null || true

# Set default workdir for tests
WORKDIR /workspace/kotlin
