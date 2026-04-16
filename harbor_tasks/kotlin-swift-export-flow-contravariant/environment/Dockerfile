FROM eclipse-temurin:17-jdk-jammy

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the Kotlin repository at the base commit
# Use filter=blob:none for faster clone, then fetch the specific commit
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git kotlin

WORKDIR /workspace/kotlin

# Fetch the base commit and checkout
RUN git fetch --depth=100 origin 7730271d0f5754fdffedf0199ab34b405dc746b0 \
    && git checkout 7730271d0f5754fdffedf0199ab34b405dc746b0 \
    && git submodule update --init --recursive --depth=1 || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-warm Gradle by downloading wrapper (optional optimization)
RUN ./gradlew --version 2>/dev/null || true

WORKDIR /workspace/kotlin
