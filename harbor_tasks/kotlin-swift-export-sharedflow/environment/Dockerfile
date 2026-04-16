FROM eclipse-temurin:21-jdk-jammy

# Install dependencies: git, python3, pip, curl
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest via pip
RUN pip3 install --break-system-packages pytest 2>/dev/null || pip3 install pytest

# Set up workdir
WORKDIR /workspace

# Clone the Kotlin repo at the base commit
# Using --depth to limit history for faster clone
RUN git clone --depth 200 --filter=blob:none \
    https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git checkout 75e54d4c71aa279aba4cc23066beb2abda5a9e69

# Create verifier log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
