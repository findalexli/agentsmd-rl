FROM eclipse-temurin:17-jdk

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone Kotlin repository at the base commit (shallow clone for speed)
# Base commit: 1d6b471bbc6a1128df5c4d69cf39b451482a9ebc
RUN git clone --filter=blob:none --depth=500 https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git checkout 1d6b471bbc6a1128df5c4d69cf39b451482a9ebc

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory to the Kotlin repo
WORKDIR /workspace/kotlin
