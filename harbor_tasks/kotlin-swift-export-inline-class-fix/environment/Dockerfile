# Kotlin Swift Export Benchmark Task
# PR: JetBrains/kotlin#5758 - Fix inline class with ref type crash

FROM eclipse-temurin:21-jdk

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone Kotlin repository at base commit
# Using --filter=blob:none to reduce clone size (shallow clone doesn't work well with old commits)
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout e5bfbbbd7f9d48f9d6039cd7d9459719d02b9b30

# Set workdir to the kotlin repo
WORKDIR /workspace/kotlin

# Pre-download Gradle wrapper to speed up subsequent builds
RUN ./gradlew --version

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
