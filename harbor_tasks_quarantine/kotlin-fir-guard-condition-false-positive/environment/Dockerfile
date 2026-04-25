FROM eclipse-temurin:11-jdk

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-install pytest
RUN pip3 install pytest -q --break-system-packages

# Clone Kotlin repository
# Using --depth=100 to have enough history for the base commit
WORKDIR /workspace
RUN git clone --depth=100 --filter=blob:none https://github.com/JetBrains/kotlin.git kotlin

WORKDIR /workspace/kotlin
# Checkout the specific base commit
RUN git fetch --depth=100 origin 94c83dce9cc665ff0b6761add7aab84ff9c77b01 && \
    git checkout 94c83dce9cc665ff0b6761add7aab84ff9c77b01

# Setup gradle wrapper permissions
RUN chmod +x ./gradlew

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
