FROM eclipse-temurin:21-jdk

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install --break-system-packages pytest pyyaml

# Set working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit (shallow clone for speed)
# Note: Kotlin repo is large, so we use --depth=1 and checkout the specific commit
RUN git clone --depth 50 --filter=blob:none https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git fetch --depth 50 origin b1cf5c86d38eaf02d1cf5187f26c23f11e94e126 && \
    git checkout b1cf5c86d38eaf02d1cf5187f26c23f11e94e126

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/kotlin
