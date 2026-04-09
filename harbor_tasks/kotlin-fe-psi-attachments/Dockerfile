FROM node:22-slim

# Install Python and dependencies for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

# Clone the Kotlin repository at base commit
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git kotlin && \
    cd kotlin && \
    git checkout 8a4eec5e568ebd8e3203fc214468259678be1135

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/kotlin
