FROM eclipse-temurin:17-jdk

# Install dependencies: git, python3, pip
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit (shallow clone for speed)
# Using base commit: 65fee3c3cad8012a6aad5df7554a1dd20dfb8d22
RUN git clone --filter=blob:none --depth=50 https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git fetch --depth=1 origin 65fee3c3cad8012a6aad5df7554a1dd20dfb8d22 && \
    git checkout 65fee3c3cad8012a6aad5df7554a1dd20dfb8d22

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
