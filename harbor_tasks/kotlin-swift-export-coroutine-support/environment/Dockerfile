FROM eclipse-temurin:21-jdk

# Install dependencies: git, python3, pytest
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Clone Kotlin repo at base commit (shallow clone for speed)
WORKDIR /workspace
RUN git clone --filter=blob:none --depth=100 https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git fetch --depth=100 origin 783211b67208a95c1695c51eb5beed9bb5bed072 && \
    git checkout 783211b67208a95c1695c51eb5beed9bb5bed072

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
