FROM maven:3.9-eclipse-temurin-17

# Install Python for pytest (including venv)
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
ARG BASE_COMMIT=18c87a604b930e8d6bcf50f2e182f5f9ceac09ab
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git checkout ${BASE_COMMIT}

# Maven plugin directory
WORKDIR /workspace/kotlin/libraries/tools/kotlin-maven-plugin

# Pre-download dependencies to speed up builds
RUN mvn dependency:go-offline -q || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
