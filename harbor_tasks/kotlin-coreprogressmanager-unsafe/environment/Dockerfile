FROM eclipse-temurin:17-jdk-noble

# Install Python, git, and patch
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git kotlin && \
    cd kotlin && \
    git checkout 65fee3c3cad8012a6aad5df7554a1dd20dfb8d22

# Pre-compile the specific file's dependencies by running a simple gradle task
WORKDIR /workspace/kotlin

# Create logs directory
RUN mkdir -p /logs/verifier
