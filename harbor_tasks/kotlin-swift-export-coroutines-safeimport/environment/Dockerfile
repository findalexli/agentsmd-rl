FROM eclipse-temurin:17-jdk-noble

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Create directory structure and fetch the specific file we need
RUN mkdir -p /workspace/kotlin/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider

# Fetch the target file at base commit using GitHub API
RUN curl -sL "https://raw.githubusercontent.com/JetBrains/kotlin/ff1ea74e2d4c120495571a5b32d7075a9e8dba07/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt" \
    -o /workspace/kotlin/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt

# Ensure log directory exists
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
