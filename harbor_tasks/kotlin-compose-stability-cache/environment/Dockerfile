# Kotlin repository with Compose compiler plugin
FROM eclipse-temurin:17-jdk

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone Kotlin repository at the base commit (shallow clone with filter)
# Base commit: 3657c00274a9252a8b71e6434cd6c63cf3770803
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git kotlin && \
    cd kotlin && \
    git checkout 3657c00274a9252a8b71e6434cd6c63cf3770803

# Set working directory to the cloned repo
WORKDIR /workspace/kotlin

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-download Gradle wrapper and dependencies to speed up test runs
RUN ./gradlew --version 2>/dev/null || true

# Default command
CMD ["bash"]
