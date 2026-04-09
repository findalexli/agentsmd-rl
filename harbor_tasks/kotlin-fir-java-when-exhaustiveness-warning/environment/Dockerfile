FROM eclipse-temurin:17-jdk

# Install dependencies: git, python3, pip, and basic tools
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest --break-system-packages || pip3 install pytest

# Create working directory
WORKDIR /workspace

# Clone Kotlin repository at the base commit
# Using shallow clone to reduce size
RUN git clone --depth=100 --filter=blob:none https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git fetch --depth=100 origin 8d783d308126447f065a2c6310e96ee90bdc832b && \
    git checkout 8d783d308126447f065a2c6310e96ee90bdc832b

# Set working directory to the Kotlin repo
WORKDIR /workspace/kotlin

# Pre-download Gradle wrapper and dependencies (optional optimization)
# RUN ./gradlew --version || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
