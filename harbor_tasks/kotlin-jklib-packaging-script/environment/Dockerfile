# Kotlin compiler repository - Gradle build script task
FROM gradle:8.5-jdk17

# Install Python for test runner
USER root
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace/kotlin

# Clone the repository at base commit (shallow clone for speed)
# Using --filter=blob:none for partial clone to save space
RUN git clone --filter=blob:none --no-checkout https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    git fetch --depth=1 origin b3980e3b7d4d1cfb4e9ad01cc26d73aa2a1c6c24 && \
    git checkout b3980e3b7d4d1cfb4e9ad01cc26d73aa2a1c6c24

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-download Gradle wrapper dependencies (optional optimization)
RUN ./gradlew --version 2>/dev/null || true

WORKDIR /workspace/kotlin
