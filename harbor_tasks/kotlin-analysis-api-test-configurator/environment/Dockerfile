FROM eclipse-temurin:21-jdk

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set up working directory
WORKDIR /workspace

# Clone Kotlin repo at base commit (shallow clone with blob filter for speed)
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout cf158c2f4a54d62787dc129cc1afdc86d08c9b9f

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
